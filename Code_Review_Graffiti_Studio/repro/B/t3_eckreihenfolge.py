"""Hinweis 3: Eckreihenfolge/Umlaufsinn wird weder in Settings noch in transform normalisiert.
Synthetisches, asymmetrisches Bild; Vergleich der Ausgabe mit transponiertem/gedrehtem Referenzbild."""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image, ImageDraw
from adjustments import Settings
from photo_prepare import transform

# 400x300, roter Block oben links, blauer Balken unten, gruener Punkt rechts Mitte
img = Image.new('RGB', (400, 300), (200, 200, 200))
d = ImageDraw.Draw(img)
d.rectangle((10, 10, 80, 60), fill=(255, 0, 0))
d.rectangle((0, 260, 399, 299), fill=(0, 0, 255))
d.ellipse((350, 140, 380, 170), fill=(0, 255, 0))
A = np.array(img)

def where(arr, rgb):
    m = np.all(np.abs(arr.astype(int) - rgb) < 60, axis=2)
    ys, xs = np.nonzero(m)
    return (round(xs.mean() / arr.shape[1], 2), round(ys.mean() / arr.shape[0], 2)) if len(xs) else None

cases = {
    'korrekt TL,TR,BR,BL': [[0, 0], [1, 0], [1, 1], [0, 1]],
    'gespiegelt TL,BL,BR,TR (Ecken 2/4 vertauscht)': [[0, 0], [0, 1], [1, 1], [1, 0]],
    'zyklisch TR,BR,BL,TL (jede Ecke eins weiter)': [[1, 0], [1, 1], [0, 1], [0, 0]],
    'zyklisch BR,BL,TL,TR': [[1, 1], [0, 1], [0, 0], [1, 0]],
}
for name, corners in cases.items():
    s = Settings(corners=corners)  # Validierung akzeptiert?
    out = np.array(transform(img, dict(corners=s.corners, rotate=0, glare_strength=0)))
    same = out.shape == A.shape and np.abs(out.astype(int) - A).max() == 0
    transp = out.shape == A.transpose(1, 0, 2).shape and np.abs(out.astype(int) - A.transpose(1, 0, 2)).max() <= 2
    print(f'{name:48s} Settings ok, Ausgabe {out.shape[1]}x{out.shape[0]}, identisch={same}, transponiert(=gespiegelt+gedreht)={transp}, '
          f'rot@{where(out,(255,0,0))} blau@{where(out,(0,0,255))} gruen@{where(out,(0,255,0))}')
print('Original: rot@', where(A, (255, 0, 0)), 'blau@', where(A, (0, 0, 255)), 'gruen@', where(A, (0, 255, 0)))
# Spiegelung pruefen: Ist die gespiegelte Ausgabe durch eine Drehung (0/90/180/270) in das Original ueberfuehrbar?
out = transform(img, dict(corners=[[0, 0], [0, 1], [1, 1], [1, 0]], rotate=0, glare_strength=0))
for r in (0, 90, 180, 270):
    o = np.array(out.rotate(r, expand=True))
    print('gespiegelt + Drehung', r, '-> gleich Original:', o.shape == A.shape and np.abs(o.astype(int) - A).max() <= 2)
