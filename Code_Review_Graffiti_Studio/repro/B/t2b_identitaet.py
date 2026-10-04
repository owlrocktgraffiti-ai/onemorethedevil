"""Vollbild-Ecken (wie nach openMask ohne Rezept): ist transform pixelidentisch?"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image
from photo_prepare import transform
rng = np.random.default_rng(0)
for W, H in [(4032, 3024), (3024, 4032), (1999, 1001), (6000, 4000)]:
    a = rng.integers(0, 256, (H, W, 3), dtype=np.uint8)
    out = np.array(transform(Image.fromarray(a), dict(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], rotate=0)))
    d = np.abs(out.astype(int) - a)
    print(f'{W}x{H}: Ausgabe {out.shape[1]}x{out.shape[0]}, max. Abweichung {d.max()}, Anteil geaenderter Pixel {(d.max(axis=2) > 0).mean():.4f}')
