"""LIES_MICH.txt:13/20 'Reflexrechtecke ... markieren' / 'Fuer neue stoerende Tags/Reflexe die Maske verwenden'.
Nicht-Abzug, Reflexrechteck gesetzt, Regler 'Reflexschleier' auf Auto (Standard): Wirkt das Rechteck?"""
import sys
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np
from PIL import Image
res = fresh_resources('glare_auto'); wd = res.parent
a = np.random.default_rng(1).integers(60, 160, (700, 1000, 3), dtype=np.uint8); a[200:400, 500:800] = np.clip(a[200:400, 500:800].astype(int) + 70, 0, 255)
Image.fromarray(a).save(wd / 'wand.png')
full = [[0, 0], [1, 0], [1, 1], [0, 1]]
outs = {}
for label, s in [('ohne Rechteck', dict(mode='klassisch', scale=1, corners=full)),
                 ('mit Rechteck, Regler Auto', dict(mode='klassisch', scale=1, corners=full, glare_regions=[[0.5, 0.28, 0.8, 0.57]])),
                 ('mit Rechteck, Regler 70 %', dict(mode='klassisch', scale=1, corners=full, glare_regions=[[0.5, 0.28, 0.8, 0.57]], values=dict(glare=70)))]:
    code, ev, err = bridge(res, 'preview', dict(source=str(wd / 'wand.png'), output=str(wd / (str(len(outs)) + '.png')), settings=s), wd)
    outs[label] = np.asarray(Image.open(ev[-1]['result']['image']).convert('L')).astype(int)
    print(f'{label:28} glare-Regler aufgeloest={ev[-1]["result"]["analysis"]["controls"]["glare"]}')
b = outs['ohne Rechteck']
for k in list(outs)[1:]: print(f'  Differenz "{k}" zu "ohne Rechteck": max {np.abs(outs[k]-b).max()}  Pixel>5: {(np.abs(outs[k]-b)>5).mean():.3f}')
