"""G2: Orakel der Tests (test_native_engine.py:26 / test_native_bridge.py:19) gegen fehlerhafte Ausgaben."""
import json, os, stat
from pathlib import Path
from PIL import Image
from vcommon import *

def oracle(size):
    w, h = size
    return w <= 1440 and h <= 1000 and w > h

setting = dict(mode='klassisch', scale=1, values=dict(contrast=30, vibrance=70, glare=50))  # wie test_native_bridge.py:17

# (a) Rezept dreht, schneidet aber nicht (Ecken = Vollbild)
res = fresh_resources('g2a'); inp = res.parent / 'in'; inp.mkdir()
src = inp / 'IMG_4363.JPG'
big = res.parent / 'tmp.png'; make_print_on_table(big, (3024, 4032))
Image.open(big).save(src, quality=95)
r = json.loads((res / 'Fotorezepte.json').read_text())
r['IMG_4363.JPG'].update(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], image_sha256=fingerprint(src))
(res / 'Fotorezepte.json').write_text(json.dumps(r))
code, ev, err = bridge(res, 'preview', dict(source=str(src), output=str(res.parent / 'crop.png'), settings=setting))
out = ev[-1]['result']; im = Image.open(out['image'])
print('(a) Vollbild-Ecken+Drehung: Groesse', im.size, '| Orakel besteht:', oracle(im.size), '| Tisch/Nachbar', table_fraction(im),
      '| executed[0]', out['analysis']['executed'][0], '| Warnungen', out['analysis']['warnings'])

# (b) Fingerabdruck passt nicht (z. B. anderer JPEG-Decoder), OCR-Engine vorhanden und sicher -> Drehung ohne Zuschnitt
res = fresh_resources('g2b'); inp = res.parent / 'in'; inp.mkdir()
src = inp / 'IMG_4363.JPG'; Image.open(big).save(src, quality=95)
stub = res / 'engine/orientation'
stub.write_text('#!' + PY + '\nimport json\nprint(json.dumps([{"rotate":0,"score":1,"characters":3},{"rotate":90,"score":20,"characters":20},{"rotate":180,"score":0,"characters":0},{"rotate":270,"score":0,"characters":0}]))\n')
stub.chmod(0o755)
code, ev, err = bridge(res, 'preview', dict(source=str(src), output=str(res.parent / 'crop.png'), settings=setting))
out = ev[-1]['result']; im = Image.open(out['image'])
print('(b) Rezept greift nicht, OCR dreht: Groesse', im.size, '| Orakel besteht:', oracle(im.size), '| Tisch/Nachbar', table_fraction(im),
      '| executed', out['analysis']['executed'][:2], '| Warnungen', out['analysis']['warnings'][:2])
