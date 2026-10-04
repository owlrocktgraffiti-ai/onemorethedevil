"""C8: Panorama im Ordnerexport. stitch() prueft alle Paare (n*(n-1)/2) und berechnet SIFT fuer jedes Paar neu,
ohne Fortschritt und ohne Abbruchpruefung. Hier: N unzusammenhaengende Fotos (wie die 23 mitgelieferten),
SIGTERM 1 s nach Beginn der Panorama-Phase (= nach dem letzten 'Fertig'-Fortschritt des letzten Fotos)."""
from common import *
from PIL import Image
import numpy as np
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12
work, res = fresh('c8')
rng = np.random.default_rng(8)
src = work / 'Eingabe'; src.mkdir()
files = []
for i in range(N):
    base = rng.integers(0, 255, (90, 120, 3), dtype=np.uint8)
    im = Image.fromarray(base).resize((1600, 1200), Image.BICUBIC)
    fine = rng.integers(-40, 40, (1200, 1600, 3))
    im = Image.fromarray(np.clip(np.array(im).astype(int) + fine, 0, 255).astype(np.uint8))
    p = src / f'wand{i:02d}.jpg'; im.save(p, quality=90); files.append(str(p))
out = work / 'Ordner_pano'
mark = {}
def on_line(proc, ev, t):
    if ev.get('type') == 'progress' and ev.get('stage', '').startswith(f'{N}/{N}') and ev.get('stage', '').endswith('Fertig'):
        mark['pano_start'] = t
        def later():
            time.sleep(1.0); proc.send_signal(signal.SIGTERM); mark['sigterm'] = time.monotonic() - T0
        import threading; threading.Thread(target=later, daemon=True).start()
T0 = time.monotonic()
r = bridge(res, 'batch', swift_export_library(files, files[0], knob(mode='klassisch', scale=1, export='panorama'), {}, out), work, on_line=on_line)
T0  # noqa
f = final(r)
last_prog = [e for e in r['events'] if e['type'] == 'progress'][-1]
print(f'N={N}: Panorama-Phase ab t={mark.get("pano_start"):.1f}s, SIGTERM bei t={mark.get("sigterm"):.1f}s, Endereignis "{f["type"]}" bei t={f["_t"]}s '
      f'(Panorama-Phase {f["_t"]-mark["pano_start"]:.1f}s ohne Fortschritt; letzter Fortschritt: {last_prog["stage"]!r} {last_prog["fraction"]})')
if f['type'] == 'result': print('Ergebnis:', {k: f['result'][k] for k in ('images', 'warnings')})
