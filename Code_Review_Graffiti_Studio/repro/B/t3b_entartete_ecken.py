"""Entartete Ecken (doppelte/kollineare Punkte), wie sie durch Ziehen und Klemmen auf 0..1 im Swift-Editor entstehen.
Prueft Settings-Validierung und transform-Ergebnis."""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image, ImageDraw
from adjustments import Settings
from photo_prepare import transform

img = Image.new('RGB', (400, 300), (200, 200, 200))
ImageDraw.Draw(img).rectangle((10, 10, 80, 60), fill=(255, 0, 0))
cases = {
    'zwei Ecken auf derselben Bildecke (2 und 3 auf (1,1))': [[0, 0], [1, 1], [1, 1], [0, 1]],
    'Ecke 2 auf Ecke 1 gezogen': [[0, 0], [0, 0], [1, 1], [0, 1]],
    'alle vier kollinear (Diagonale)': [[0, 0], [.3, .3], [.6, .6], [1, 1]],
    'drei kollinear auf Oberkante': [[0, 0], [.5, 0], [1, 0], [.5, 1]],
    'alle auf einem Punkt': [[.5, .5]] * 4,
}
for name, c in cases.items():
    try:
        Settings(corners=c); val = 'Settings akzeptiert'
    except Exception as e:
        val = 'Settings: ' + type(e).__name__ + ': ' + str(e)
    try:
        out = np.array(transform(img, dict(corners=c, rotate=0, glare_strength=0)))
        res = f'transform -> {out.shape[1]}x{out.shape[0]}, mittlere Helligkeit {out.mean():.1f}, Anteil schwarz {(out.max(axis=2) == 0).mean():.2f}'
    except Exception as e:
        res = 'transform: ' + type(e).__name__ + ': ' + str(e)[:120]
    print(f'{name:55s} | {val} | {res}')
