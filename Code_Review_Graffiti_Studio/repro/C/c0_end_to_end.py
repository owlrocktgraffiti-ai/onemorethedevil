"""C0: End-to-End native_bridge preview/export/batch mit synthetischen Bildern (Engine/realesrgan fehlen).
Request-JSON wie Swift (KnobState.json). Prueft stdout-Ereignisse, Dateien, CSV, Bericht, ZIP."""
from common import *
from PIL import Image
import numpy as np, zipfile, csv
work, res = fresh('c0')
rng = np.random.default_rng(0)
src = work / 'Eingabe'; (src / 'Unter').mkdir(parents=True)
Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((800, 600)).save(src / 'wand.jpg')
Image.fromarray(rng.integers(0, 255, (40, 120, 3), dtype=np.uint8)).resize((1500, 500)).save(src / 'Unter' / 'breit.png')
(src / 'kaputt.jpg').write_bytes(b'kein jpeg')
k = knob()
print('== preview')
r = bridge(res, 'preview', dict(source=str(src / 'wand.jpg'), output=str(work / 'tmp' / 'p.png'), settings=knob_json(k)), work)
print('rc', r['returncode'], 'Typen', [e['type'] for e in r['events']], 'final', {kk: v for kk, v in final(r).items() if kk != 'result'})
res_ = final(r)['result']; print('Vorschaubild', Image.open(res_['image']).size, 'backend', res_['analysis']['effective_backend'], 'warnings', res_['analysis']['warnings'])
print('== export (instagram)')
out = work / 'Ausgabe' / 'Foto_1'
r = bridge(res, 'export', dict(source=str(src / 'Unter' / 'breit.png'), output=str(out / 'breit.png'), settings=knob_json(knob(export='instagram'))), work)
f = final(r); print('rc', r['returncode'], 'final', f['type'], {kk: f['result'][kk] for kk in ('images', 'zip', 'folder')})
print('Dateien', tree(out))
with zipfile.ZipFile(f['result']['zip']) as z: print('ZIP', z.namelist())
print('== batch (3 Dateien, 1 defekt)')
files = [str(src / 'wand.jpg'), str(src / 'Unter' / 'breit.png'), str(src / 'kaputt.jpg')]
req = swift_export_library(files, files[0], k, {}, work / 'Ausgabe' / 'Ordner_1')
r = bridge(res, 'batch', req, work)
f = final(r); print('rc', r['returncode'], 'Ereignisse', [(e['type'], e.get('stage', e.get('message', ''))[:60]) for e in r['events']])
print('Ergebnis', {kk: v for kk, v in f['result'].items()})
print('Dateien', tree(work / 'Ausgabe' / 'Ordner_1'))
print('CSV:'); print((work / 'Ausgabe' / 'Ordner_1' / 'Protokoll.csv').read_text(encoding='utf-8-sig'))
with zipfile.ZipFile(f['result']['zip']) as z: print('ZIP-Eintraege', len(z.namelist()))
plan = json.loads((work / 'Ausgabe' / 'Ordner_1' / '01_wand.json').read_text())
print('Plan output_path:', plan['output_path'])
