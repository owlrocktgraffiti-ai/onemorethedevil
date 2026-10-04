"""Laufzeit von transform mit Retuschstrichen auf Vollaufloesung (die Vorschau ruft transform ebenfalls auf Vollaufloesung auf,
erst danach wird auf 1440x1000 verkleinert)."""
import sys, pathlib, time
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image
from photo_prepare import transform
rng = np.random.default_rng(0)
img = Image.fromarray(rng.integers(0, 256, (3024, 4032, 3), dtype=np.uint8))
full = [[0, 0], [1, 0], [1, 1], [0, 1]]
t = time.time(); transform(img, dict(corners=full, rotate=0)); print(f'ohne Striche: {time.time() - t:.2f} s')
for r, n in [(0.02, 1), (0.05, 1), (0.05, 3)]:
    strokes = [dict(points=[[0.1 + 0.8 * i / 40, 0.2 + 0.25 * k] for i in range(41)], radius=r) for k in range(n)]
    t = time.time(); transform(img, dict(corners=full, rotate=0, retouch_strokes=strokes, retouch_strength=1)); dt = time.time() - t
    print(f'{n} Strich(e) quer ueber das Bild, Radius {int(r * 100)} %: {dt:.2f} s')
