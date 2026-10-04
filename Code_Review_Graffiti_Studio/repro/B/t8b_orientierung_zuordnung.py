"""Hinweis 8: Zuordnung [.up,.left,.down,.right] -> [0,90,180,270] in engine/orientation.swift.
CGImagePropertyOrientation-Rohwerte: up=1, down=3, right=6, left=8 (= EXIF-Werte). Vision bekommt die Orientierung,
die das Bild aufrecht macht. Pruefung: EXIF-Wert -> exif_transpose ergibt dasselbe wie PIL rotate(Grad) (gegen Uhrzeigersinn)."""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image, ImageOps
a = np.random.default_rng(3).integers(0, 256, (40, 60, 3), dtype=np.uint8); im = Image.fromarray(a)
for name, exif_value, degrees in [('.up', 1, 0), ('.left', 8, 90), ('.down', 3, 180), ('.right', 6, 270)]:
    e = Image.Exif(); e[0x0112] = exif_value; im.info['exif'] = e.tobytes(); im._exif = None
    t = ImageOps.exif_transpose(im)
    r = im.rotate(degrees, expand=True)
    print(f'{name:7s} (EXIF {exif_value}) -> aufrecht == PIL rotate({degrees}): {np.array_equal(np.array(t), np.array(r))}')
