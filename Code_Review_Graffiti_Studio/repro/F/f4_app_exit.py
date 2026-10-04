"""F4: App-Ende waehrend eines Ordnerexports.
 a) normales Beenden (applicationWillTerminate -> shutdown -> SIGTERM, danach ist das Lese-Ende der Pipe weg)
 b) App-Absturz/Sofort beenden (kein SIGTERM, nur Pipe geschlossen)
Beobachtet: Prozessdauer nach App-Ende, Exitcode, stderr, Inhalt des Ausgabeordners (Bilder/CSV/ZIP).
Aufruf: venv/bin/python repro/F/f4_app_exit.py
"""
import signal, time
from common import *

work, res = fresh('f4')
files = [str(noise_photo(work / f'IMG_{i}.jpg', size=(3000, 2250), seed=i)) for i in range(5)]


def scenario(label, send_sigterm):
    out = work / f'Ordner_{label}'
    b = Bridge(res, 'batch', dict(files=files, output=str(out), settings=dict(mode='klassisch', scale=1)), work)
    done = []
    def on_event(br, ev):
        # App endet, waehrend Foto 2 gerade gerechnet wird
        if not done and ev.get('type') == 'progress' and ev.get('stage', '').startswith('2/5') and 'Vorbereitung' in ev.get('stage', ''):
            done.append(br.t())
            if send_sigterm:
                br.proc.send_signal(signal.SIGTERM); br.events.append({'type': '<SIGTERM gesendet>', '_t': br.t()})
            br.close_stdout()
    b.callbacks.append(on_event)
    b.wait(timeout=300)
    print(f'=== {label}')
    print(b.summary(stages=False))
    print(f'App-Ende bei {done}; Python-Ende nach {b.seconds}s (lief {round(b.seconds - done[0], 2)} s ohne App weiter); Exitcode {b.returncode}')
    tail = [l for l in b.stderr.strip().splitlines() if l.strip()]
    print('stderr letzte Zeilen:', tail[-3:])
    print('Ausgabeordner:', sorted(p.name for p in out.iterdir()) if out.exists() else '-')
    print('ZIP:', out.with_suffix('.zip').exists(), '| Protokoll.csv:', (out / 'Protokoll.csv').exists())
    if (out / 'Protokoll.csv').exists():
        print((out / 'Protokoll.csv').read_text(encoding='utf-8-sig'))


scenario('normal_beendet', True)
scenario('absturz', False)
