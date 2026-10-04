"""G17-Zusatz: per_photo-Schluessel (Swift: url.path, unaufgeloest) vs. Python-Lookup str(source.resolve()) (studio_backend.py:89)."""
import json, os
from PIL import Image
from vcommon import *
res = fresh_resources('g17'); real = res.parent / 'echt'; real.mkdir(); Image.new('RGB', (800, 600), (90, 100, 120)).save(real / 'f.png')
link = res.parent / 'verknuepft'; os.symlink(real, link)
src = str(link / 'f.png')
per = {src: dict(mode='klassisch', corners=[[0, 0], [.5, 0], [.5, .5], [0, .5]])}
code, ev, err = bridge(res, 'batch', dict(files=[src], output=str(res.parent / 'out'), settings=dict(mode='klassisch'), per_photo=per))
plan = json.loads((res.parent / 'out/01_f.json').read_text())
print('Ordnerpfad mit Symlink: Ecken im Ergebnisplan =', plan['settings']['corners'], '| Ausgabe', Image.open(res.parent / 'out/01_f.png').size, '(erwartet halbe Breite/Hoehe)')
