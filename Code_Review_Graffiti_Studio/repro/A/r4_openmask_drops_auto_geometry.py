"""A4: openMask() uebernimmt nur plan['preparation']; fehlt sie (Drehung kommt aus der Texterkennung
plan['rotation'], schwarze Balken aus plan['border_crop']), setzt Swift corners=Vollbild und rotation=nil.
Schon "Ecken & Maske bearbeiten..." + "Uebernehmen" ohne jede Aenderung schickt corners=[[0,0],[1,0],[1,1],[0,1]]
und use_saved_retouches=false -> adjustments.py:94-102 verwirft rotation und border_crop.
"""
from common import *
from PIL import Image
import numpy as np
work, res = fresh_resources('r4')
stub_orientation(res, sleep=0, rotate=90)     # sichere OCR-Drehung um 90 Grad
rng = np.random.default_rng(4)
W, H = 1400, 1000
canvas = np.zeros((H, W, 3), np.uint8)       # gleichmaessige schwarze Balken rundum
content = np.array(Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((W - 200, H - 300), Image.BICUBIC))
canvas[150:H - 150, 100:W - 100] = content
src = work / 'Zug.png'; Image.fromarray(canvas).save(src)

def run(settings, tag):
    ev = bridge(res, 'preview', dict(source=str(src), output=str(work / f'{tag}.png'), settings=settings), work)['events'][-1]
    plan = ev['result']['analysis']
    with Image.open(ev['result']['image']) as im: size = im.size
    black = (np.array(Image.open(ev['result']['image']).convert('L')) <= 8).mean()
    print(f'{tag:28s} Ausgabe {size}, schwarzer Anteil {100*black:5.1f} %, rotation={plan.get("rotation")}, border_crop={plan.get("border_crop")}, executed={plan.get("executed")[:2]}')

run({}, 'Automatik')
run(dict(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], use_saved_retouches=False), 'nach openMask+Uebernehmen')
