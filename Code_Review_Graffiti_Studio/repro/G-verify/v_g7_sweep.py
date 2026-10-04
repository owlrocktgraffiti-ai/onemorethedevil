"""G7: Variation der Szene -> wann greift der automatische Papierkanten-Zuschnitt bei einem Nicht-Abzug?"""
import sys; from vcommon import *
sys.path.insert(0, str(fresh_resources('g7s')))
import numpy as np
from PIL import Image, ImageDraw
from photo_prepare import recipe
from analysis import paper_confidence
rng = np.random.default_rng(7)
def scene(bg, car, gap, under=True, noise=12):
    w, h = 1500, 1000
    a = np.zeros((h, w, 3), np.uint8); a[:] = bg
    a = np.clip(a.astype(int) + rng.integers(-noise, noise+1, a.shape), 0, 255).astype(np.uint8)
    im = Image.fromarray(a); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = int(.05*w), int(.13*h), int(.95*w), int(.80*h)
    d.rectangle((x0, y0, x1, y1), fill=car)
    for i in range(6):
        cx = x0 + 60 + i*210
        d.ellipse((cx, y0+80, cx+170, y1-90), fill=[(230, 40, 40), (250, 200, 30), (40, 160, 230)][i % 3], outline=(0, 0, 0), width=6)
    if under: d.rectangle((x0+40, y1+gap, x1-40, y1+gap+45), fill=(30, 30, 30))
    return im
for bg, bgname in [((175, 100, 60), 'Backstein warm'), ((120, 150, 190), 'Himmel gleichmaessig'), ((128, 128, 128), 'Beton grau')]:
    for car, carname in [((195, 198, 205), 'silber'), ((150, 30, 30), 'rot')]:
        for gap, under in [(0, True), (5, True), (40, True), (0, False)]:
            im = scene(bg, car, gap, under)
            cfg, reason = recipe(im, 'x.png')
            conf = paper_confidence(im, cfg) if reason.startswith('Papierkanten') else None
            print(f'{bgname:22} Wagen {carname:6} Fahrwerk {"Abstand %2dpx" % gap if under else "keins     "} -> {reason[:28]:28} conf={conf} {"ZUSCHNITT" if conf and conf >= .86 else ""}')
