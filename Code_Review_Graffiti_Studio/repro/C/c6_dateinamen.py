"""C6: Dateinamen im Einzel- und Ordnerexport: Punkte, Unicode (NFD wie macOS), Komma/Leerzeichen, sehr lange Namen.
Hilfsdateien '<ziel>.working.png' (studio_backend.py:39) und '<plan>.json.tmp' (:47) verlaengern den Namen um 12 bzw. 9 Byte,
im Ordnerexport kommt das Praefix '01_' dazu. NAME_MAX = 255 Byte (APFS wie ext4)."""
from common import *
from PIL import Image
import numpy as np, unicodedata, zipfile
work, res = fresh('c6')
rng = np.random.default_rng(6)
src = work / 'Eingabe'; src.mkdir()
def mk(name):
    p = src / name; Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((640, 480)).save(p); return str(p)
names = ['foto.v2.final.jpg', unicodedata.normalize('NFD', 'Bahnhof Zürich – Ölwagen 🚂.jpg'), 'crak, syck.jpg',
         'L' * 236 + '.jpg', 'M' * 237 + '.jpg', 'S' * 240 + '.jpg', 'S' * 251 + '.jpg']
files = [mk(n) for n in names]
out = work / 'Ordner_1'
f = final(bridge(res, 'batch', swift_export_library(files, files[0], knob(mode='klassisch', scale=1), {}, out), work))
print('Ordnerexport:', f['type'], {k: f['result'][k] for k in ('images', 'total', 'warnings')})
for row in (out / 'Protokoll.csv').read_text(encoding='utf-8-sig').splitlines()[1:]:
    cols = row.split(',')
    print('  CSV:', ('…' + cols[0][-40:]) if len(cols[0]) > 40 else cols[0], '|', cols[-2], '|', cols[-1][:70])
with zipfile.ZipFile(f['result']['zip']) as z: print('  ZIP-Namen (gekuerzt):', [n[:40] for n in z.namelist() if n.endswith('.png')])
print('Einzelexport (Swift: <Ausgabe>/Foto_<stempel>/<stem>.png):')
for n, p in zip(names, files):
    stem = Path(p).stem
    r = bridge(res, 'export', dict(source=p, output=str(work / ('Foto_' + str(time.time_ns())) / (stem + '.png')), settings=knob_json(knob(mode='klassisch', scale=1))), work)
    e = final(r)
    print(f'  Stem {len(stem.encode()):3d} Byte: {e["type"]}', '' if e['type'] == 'result' else e.get('message', '')[:90] or r['stderr'][-120:])
