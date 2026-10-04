"""G7: Einfluss des Bildrauschens auf paper_confidence."""
import sys
from vcommon import *
sys.path.insert(0, str(fresh_resources('g7s2')))
import numpy as np
from PIL import Image, ImageDraw
from photo_prepare import recipe
from analysis import paper_confidence
rng = np.random.default_rng(7)
def scene(bg, car, gap, under=True, noise=12, mono=False):
    w, h = 1500, 1000
    a = np.zeros((h, w, 3), np.uint8); a[:] = bg
    n = rng.integers(-noise, noise+1, (h, w, 1) if mono else (h, w, 3))
    a = np.clip(a.astype(int) + n, 0, 255).astype(np.uint8)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = int(.05*w), int(.13*h), int(.95*w), int(.80*h)
    d.rectangle((x0, y0, x1, y1), fill=car)
    for i in range(6):
        cx = x0 + 60 + i*210
        d.ellipse((cx, y0+80, cx+170, y1-90), fill=[(230, 40, 40), (250, 200, 30), (40, 160, 230)][i % 3], outline=(0, 0, 0), width=6)
    if under: d.rectangle((x0+40, y1+gap, x1-40, y1+gap+45), fill=(30, 30, 30))
    return im
for noise in (0, 4, 8, 12):
    for mono in (False, True):
        for bg, bgname in [((175, 100, 60), 'Backstein warm'), ((128, 128, 128), 'Beton grau')]:
            im = scene(bg, (195, 198, 205), 40, True, noise, mono)
            cfg, reason = recipe(im, 'x.png'); conf = paper_confidence(im, cfg) if reason.startswith('Papierkanten') else None
            print(f'Rauschen +-{noise:2} {"einkanalig" if mono else "je Kanal  "} {bgname:15} -> conf={conf} {"ZUSCHNITT" if conf and conf >= .86 else ""}')
