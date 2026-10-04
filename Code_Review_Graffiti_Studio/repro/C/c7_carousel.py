"""C7: exports.carousel – Slide-Anzahl/Hoehe passen nicht zusammen. Fuer Seitenverhaeltnisse >2 und >2.6 entstehen
Slides, die ueberwiegend schwarz sind. Bild = gleichmaessig grau (kein Schwarz im Motiv)."""
from common import *
work, res = fresh('c7')
sys.path.insert(0, str(res))
from exports import carousel
from PIL import Image
import numpy as np
for w, h in [(2000, 1000), (2100, 1000), (2500, 1000), (2700, 1000), (3000, 1000), (4000, 1000), (6000, 1000), (1000, 1250), (1500, 1000)]:
    im = Image.new('RGB', (w, h), (128, 128, 128))
    out = work / f'{w}x{h}'
    n = carousel(im, out)
    fr = []
    for i in range(n):
        a = np.array(Image.open(out / f'Slide_{i+1:02d}.jpg').convert('L'))
        fr.append(round(float((a < 20).mean()) * 100, 1))
    sz = Image.open(out / 'Slide_01.jpg').size
    print(f'Verhaeltnis {w/h:4.2f}: {n} Slides a {sz}, Schwarzanteil je Slide % {fr}; Motivpixel genutzt: {round(float((np.array(Image.open(out/"Panorama_Gemeinsame_Basis.png").convert("L"))>=20).mean())*100,1)} % der Flaeche')
