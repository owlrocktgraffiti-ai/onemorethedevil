"""Hilfsfunktionen Bereich F (Prozessprotokoll, Signale, Abbruch, Laufzeit).

Alle Tests arbeiten auf Kopien unter repro/F/work/<name>/Resources; pkg/ bleibt unveraendert.
Die Bruecke wird wie in GraffitiStudio.swift:run gestartet: stdout=Pipe (zeilenweise JSON),
stderr=Datei, Umgebung + PYTHONDONTWRITEBYTECODE=1.
"""
from pathlib import Path
import json, os, shutil, signal, subprocess, sys, threading, time

BASE = Path('/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad')
PKG_RES = BASE / 'pkg/Graffiti Studio.app/Contents/Resources'
HERE = Path(__file__).resolve().parent
PY = str(BASE / 'venv/bin/python')


def fresh(name):
    work = HERE / 'work' / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    res = work / 'Resources'
    shutil.copytree(PKG_RES, res, ignore=shutil.ignore_patterns('__pycache__'))
    return work, res


def stub_orientation(res, sleep=0.0, rotate=0, confident=False):
    """Einzelprozess-Stub fuer engine/orientation (wie das echte Swift-Programm: ein Prozess)."""
    scores = [dict(rotate=rotate, score=30 if confident else 1, characters=20 if confident else 1),
              dict(rotate=(rotate + 180) % 360, score=1, characters=1)]
    p = res / 'engine/orientation'
    p.write_text(f'#!{PY}\nimport time,json,sys\ntime.sleep({sleep})\nsys.stdout.write({json.dumps(json.dumps(scores))})\n')
    p.chmod(0o755)
    return p


def stub_realesrgan(res, behaviour='sleep', sleep=30):
    """Stub fuer engine/realesrgan-ncnn-vulkan.
    sleep      : schlaeft (kooperativ bei SIGTERM)
    ignore     : ignoriert SIGTERM und schlaeft
    grandchild : startet einen Enkelprozess (sleep) und wartet
    ok         : skaliert Eingabe x4 und schreibt Ausgabe
    """
    p = res / 'engine/realesrgan-ncnn-vulkan'
    body = f'''#!{PY}
import sys,time,signal,subprocess
args=sys.argv[1:];inp=args[args.index('-i')+1];out=args[args.index('-o')+1]
print('stub realesrgan start',flush=True)
b={behaviour!r}
if b=='ignore':signal.signal(signal.SIGTERM,signal.SIG_IGN)
if b=='grandchild':
    subprocess.Popen(['sleep','{sleep}.5'])  # MARKER-ENKEL
if b=='ok':
    from PIL import Image
    im=Image.open(inp);im.resize((im.width*4,im.height*4)).save(out);sys.exit(0)
time.sleep({sleep})
'''
    p.write_text(body)
    p.chmod(0o755)
    (res / 'engine/models').mkdir(exist_ok=True)
    return p


def procs_matching(text):
    """Liste (pid, cmdline) aller laufenden Prozesse, deren Kommandozeile text enthaelt."""
    found = []
    for d in Path('/proc').iterdir():
        if not d.name.isdigit():
            continue
        try:
            cmd = (d / 'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace').strip()
            stat = (d / 'stat').read_text().split()
        except OSError:
            continue
        if text in cmd and stat[2] != 'Z':
            found.append((int(d.name), cmd, int(stat[3])))  # pid, cmd, ppid
    return found


class Bridge:
    """Startet native_bridge.py wie BridgeJob in GraffitiStudio.swift und liest Ereignisse mit Zeitstempel."""

    def __init__(self, res, command, request, workdir, env=None, python=PY, extra_args=()):
        self.workdir = Path(workdir)
        self.req = self.workdir / f'{command}_{time.time_ns()}.json'
        # Swift schreibt JSONSerialization-Daten (UTF-8) – hier ebenfalls UTF-8-Bytes
        self.req.write_bytes(json.dumps(request, ensure_ascii=False, indent=1).encode('utf-8'))
        self.errpath = self.req.with_suffix('.log')
        e = dict(os.environ if env is None else env)
        e['PYTHONDONTWRITEBYTECODE'] = '1'
        self.err = open(self.errpath, 'wb')
        self.t0 = time.monotonic()
        self.proc = subprocess.Popen([python, *extra_args, str(Path(res) / 'native_bridge.py'), command, '--request', str(self.req)],
                                     stdout=subprocess.PIPE, stderr=self.err, env=e)
        self.events = []
        self.raw = []
        self.callbacks = []
        self.reader = threading.Thread(target=self._read, daemon=True)
        self.reader.start()

    def t(self):
        return round(time.monotonic() - self.t0, 2)

    def _read(self):
        buf = b''
        try:
            while True:
                chunk = os.read(self.proc.stdout.fileno(), 65536)
                if not chunk:
                    break
                buf += chunk
                while b'\n' in buf:
                    line, buf = buf.split(b'\n', 1)
                    self.raw.append(line)
                    try:
                        ev = json.loads(line.decode('utf-8'))  # Swift: JSONSerialization erwartet UTF-8
                    except (ValueError, UnicodeDecodeError):
                        ev = {'type': '<von Swift verworfen>', 'raw': line[:200]}
                    ev['_t'] = self.t()
                    self.events.append(ev)
                    for cb in list(self.callbacks):
                        cb(self, ev)
        except OSError:
            pass  # Lese-Ende geschlossen (App-Absturz simuliert)

    def signal_at(self, seconds, sig=signal.SIGTERM):
        def run():
            time.sleep(seconds)
            if self.proc.poll() is None:
                self.proc.send_signal(sig)
                self.events.append({'type': f'<{signal.Signals(sig).name} gesendet>', '_t': self.t()})
        threading.Thread(target=run, daemon=True).start()

    def close_stdout(self):
        """Simuliert App-Absturz/-Ende: Lese-Ende der Pipe schliessen."""
        self.events.append({'type': '<stdout-Pipe geschlossen>', '_t': self.t()})
        os.close(self.proc.stdout.fileno())

    def wait(self, timeout=600):
        rc = self.proc.wait(timeout=timeout)
        self.seconds = self.t()
        self.reader.join(timeout=2)
        self.err.close()
        self.returncode = rc
        self.stderr = self.errpath.read_text(errors='replace')
        return self

    def summary(self, stages=True):
        out = []
        for e in self.events:
            k = e.get('type')
            if k == 'progress' and stages:
                out.append(f"{e['_t']:>6}s progress {e.get('stage')} {round(e.get('fraction', 0), 3)}")
            elif k == 'progress':
                continue
            elif k == 'result':
                out.append(f"{e['_t']:>6}s result keys={sorted(e['result'])}")
            else:
                d = {x: y for x, y in e.items() if x not in ('_t',)}
                out.append(f"{e['_t']:>6}s {json.dumps(d, ensure_ascii=False, default=str)[:300]}")
        return '\n'.join(out)


def swift_error_display(stderr_text, final_event=None):
    """Was GraffitiStudio.swift im Warnhinweis zeigt (fail(...) + Label .lineLimit(2))."""
    if final_event is not None and final_event.get('type') == 'error':
        text = final_event.get('message', 'Bearbeitung fehlgeschlagen')
    else:
        text = 'Bildverarbeitung ohne Ergebnis beendet' if not stderr_text else stderr_text[-2000:]
    return '\n'.join(text.split('\n')[:2])


def noise_photo(path, size=(1600, 1200), seed=1, quality=90):
    import numpy as np
    from PIL import Image
    rng = np.random.default_rng(seed)
    small = rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)
    Image.fromarray(small).resize(size, Image.BICUBIC).save(path, quality=quality)
    return path
