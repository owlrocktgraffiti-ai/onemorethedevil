"""G8: Bildvorschlaege fuer Mehrfach-Scans im App-Pfad (batch/export); G9: Markierung von review_regions im Vergleichsbild."""
import json, zipfile, subprocess, os
import numpy as np
from PIL import Image, ImageDraw
from vcommon import *
res = fresh_resources('g89'); inp = res.parent / 'in'; inp.mkdir()
rng = np.random.default_rng(2)
# Dreifach-Scan 3000x900 mit weissen Trennstreifen
a = rng.integers(30, 200, (900, 3000, 3)).astype(np.uint8)
for s in (980, 1990): a[:, s:s+30] = 255
scan = inp / 'scan_drei.png'; Image.fromarray(a).save(scan)
# Foto mit hellem Blitzfleck
b = np.full((800, 1200, 3), (60, 70, 90), np.uint8); b = np.clip(b.astype(int) + rng.integers(-8, 9, b.shape), 0, 255).astype(np.uint8)
im = Image.fromarray(b); ImageDraw.Draw(im).ellipse((520, 300, 680, 460), fill=(255, 255, 255)); flash = inp / 'blitz.png'; im.save(flash)
settings = dict(mode='klassisch', values={})
out = res.parent / 'batch'
code, ev, err = bridge(res, 'batch', dict(files=[str(scan), str(flash)], output=str(out), settings=settings))
print('batch exit', code, ev[-1]['type'])
p1 = json.loads((out / '01_scan_drei.json').read_text())
print('G8 panel_candidates:', p1.get('panel_candidates'), '| Warnung:', [w for w in p1['warnings'] if 'Fotos' in w])
print('G8 Dateien im Ausgabeordner:', sorted(x.relative_to(out).as_posix() for x in out.rglob('*') if x.is_file()))
print('G8 Bildvorschlaege im ZIP:', [n for n in zipfile.ZipFile(str(out) + '.zip').namelist() if 'Bildvorschlag' in n])
code, ev, err = bridge(res, 'export', dict(source=str(scan), output=str(res.parent / 'einzel/scan.png'), settings=settings))
print('G8 Einzelexport Dateien:', sorted(x.name for x in (res.parent / 'einzel').rglob('*')))
# CLI zum Vergleich
cli = res.parent / 'cli'
r = subprocess.run([PY, str(res / 'graffiti.py'), '--input', str(inp), '--output', str(cli), '--mode', 'klassisch'], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
print('G8 CLI exit', r.returncode, 'Bildvorschlaege:', sorted(x.name for x in cli.rglob('Bildvorschlag_*')))
def yellow(p):
    c = np.array(Image.open(p).convert('RGB')).astype(int)
    return int(((c[..., 0] > 200) & (c[..., 1] > 170) & (c[..., 2] < 110)).sum())
p2 = json.loads((out / '02_blitz.json').read_text())
print('G9 review_regions:', p2.get('review_regions'), '| Warnungen:', [w for w in p2['warnings'] if 'markiert' in w or 'Reflex' in w])
print('G9 gelbe Pixel App-Vergleichsbild 02_Vergleich.jpg:', yellow(out / '02_Vergleich.jpg'), '| CLI 02_Vergleich.jpg:', yellow(cli / '01_Vergleich.jpg'), '(CLI-Reihenfolge alphabetisch: 01=blitz)')
