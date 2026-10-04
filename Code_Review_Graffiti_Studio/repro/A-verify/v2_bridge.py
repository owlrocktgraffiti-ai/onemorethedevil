"""Gegenpruefung ueber den echten Prozessweg native_bridge.py (A1, A7, A9, A13, A19)."""
import sys, json, os, subprocess, time, signal, shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
R = HERE / 'Resources'; PY = sys.executable
W = HERE / 'work'; shutil.rmtree(W, ignore_errors=True); W.mkdir()
import numpy as np
from PIL import Image

def make(path, size=(1600, 1200), seed=0):
    rng = np.random.default_rng(seed); a = rng.integers(40, 220, (size[1], size[0], 3), dtype=np.uint8)
    a[100:300, 200:900] = (230, 40, 40); Image.fromarray(a).save(path, quality=92); return path

def bridge(cmd, req, sig_after=None):
    rq = W / f'req_{time.time_ns()}.json'; rq.write_text(json.dumps(req))
    err = open(W / 'stderr.log', 'w')
    t = time.monotonic(); p = subprocess.Popen([PY, str(R / 'native_bridge.py'), cmd, '--request', str(rq)], stdout=subprocess.PIPE, stderr=err, text=True)
    if sig_after is not None:
        time.sleep(sig_after); p.send_signal(signal.SIGTERM)
    out, _ = p.communicate(); err.close()
    ev = [json.loads(l) for l in out.splitlines() if l.strip()]
    return p.returncode, ev, (W / 'stderr.log').read_text(), time.monotonic() - t

def S(**kw):
    d = dict(values={}, profile='auto', mode='klassisch', scale=1, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])
    d.update(kw); return d

a = make(W / 'a.jpg', seed=1); b = make(W / 'b.jpg', seed=2)
cross = [[0, 0], [1, 1], [1, 0], [0, 1]]

print('=== A7/A13: Vorschau mit gekreuzten Ecken ===')
code, ev, err, _ = bridge('preview', dict(source=str(a), output=str(W / 'p.png'), settings=S(corners=cross)))
print('  Exitcode', code, '| JSON-Ereignisse:', [e['type'] for e in ev], '| stderr Bytes:', len(err))
lines = err.strip().splitlines()
print('  Swift zeigt (suffix(2000), lineLimit 2):', err[-2000:].splitlines()[:2])
print('  letzte Zeile:', lines[-1])

print('=== A7: Ordnerexport, fremder ungueltiger per_photo-Eintrag ===')
code, ev, err, _ = bridge('batch', dict(files=[str(a), str(b)], output=str(W / 'Ordner_1'), settings=S(), per_photo={'/irgendwo/alt/x.jpg': S(corners=cross)}))
print('  Exitcode', code, '| letztes Ereignis:', ev[-1] if ev else None, '| Ausgabe existiert:', (W / 'Ordner_1').exists())

print('=== A9: per_photo-Schluessel ueber Symlink-Pfad ===')
real = W / 'real'; real.mkdir(); make(real / 'c.jpg', size=(1600, 1000), seed=3)
link = W / 'link'; link.symlink_to(real)
for label, key in [('Symlink-Pfad (wie Swift)', str(link / 'c.jpg')), ('aufgeloest', str((link / 'c.jpg').resolve()))]:
    out = W / f'Ordner_sym_{label[:4]}'
    code, ev, err, _ = bridge('batch', dict(files=[str(link / 'c.jpg')], output=str(out), settings=S(), per_photo={key: S(rotation=90)}))
    png = next(out.glob('01_*.png'))
    print(f'  {label}: Ausgabe {Image.open(png).size} ->', 'Drehung angewendet' if Image.open(png).size[1] > Image.open(png).size[0] else 'Drehung IGNORIERT')

print('=== A1: SIGTERM waehrend Ordnerexport (nach erstem Foto) ===')
files = [str(make(W / f'z{i}.jpg', size=(3000, 2200), seed=10 + i)) for i in range(4)]
# erste Dauer messen
code, ev, err, dt1 = bridge('preview', dict(source=files[0], output=str(W / 'q.png'), settings=S()))
out = W / 'Ordner_abbruch'
code, ev, err, dt = bridge('batch', dict(files=files, output=str(out), settings=S(), per_photo={}), sig_after=dt1 * 1.6)
print(f'  SIGTERM nach {dt1*1.6:.1f}s, Ende nach {dt:.1f}s, Exit {code}, letztes Ereignis {ev[-1]["type"] if ev else None}')
print('  Inhalt:', sorted(p.name for p in out.iterdir()), '| ZIP:', out.with_suffix('.zip').exists())

print('=== A19: zwei Vorschauen nacheinander ===')
for c in (10, 20):
    code, ev, err, dt = bridge('preview', dict(source=files[0], output=str(W / f'v{c}.png'), settings=S(values={'contrast': c})))
    print(f'  contrast={c}: {dt:.2f}s, Stufen', [e['stage'] for e in ev if e['type'] == 'progress'])
