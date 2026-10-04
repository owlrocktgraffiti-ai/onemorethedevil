"""A3/A4: openMask() ohne fertige Analyse (plans[selected]==nil, openMask bricht die laufende
Erstvorschau selbst per cancel() ab) setzt corners=Vollbild und laesst rotation=nil.
  (a) Uebernehmen ohne Aenderung -> Python ersetzt die Rezept-Ecken durch das Vollbild (Tisch/Nachbarabzuege bleiben).
  (b) Maskenbild ('prepare') nutzt rotation nil -> 0 (native_bridge.py:36), der Render aber die Rezeptdrehung
      90 (adjustments.py:97-99) -> Retuschstriche/Reflexbereiche landen an einer anderen Bildstelle.
Ein synthetisches Abzugsfoto bekommt in der KOPIE von Fotorezepte.json ein Rezept wie IMG_4363 (rotate 90).
"""
from common import *
from PIL import Image, ImageDraw
import numpy as np, sys
work, res = fresh_resources('r3')
sys.path.insert(0, str(res))
from analysis import digest_image

rng = np.random.default_rng(3)
W, H = 1200, 1600                                    # Hochformat wie 3024x4032
table = np.zeros((H, W, 3), np.uint8); table[:] = (150, 100, 60)          # "Tisch"
img = Image.fromarray(table)
print_area = Image.fromarray(rng.integers(0, 255, (80, 60, 3), dtype=np.uint8)).resize((int(W * .80), int(H * .88)), Image.BICUBIC)
img.paste(print_area, (int(W * .05), int(H * .05)))
src = work / 'Abzug.jpg'; img.save(src, quality=95)
from graffiti import read_image
sha = digest_image(read_image(src))
recipes = json.loads((res / 'Fotorezepte.json').read_text())
corners = [[0.05, 0.05], [0.85, 0.05], [0.85, 0.93], [0.05, 0.93]]
recipes['Abzug.jpg'] = dict(corners=corners, rotate=90, glare_strength=0.62, source_size=[W, H], image_sha256=sha)
(res / 'Fotorezepte.json').write_text(json.dumps(recipes, indent=2))

def size(path):
    with Image.open(path) as im: return im.size

auto = bridge(res, 'preview', dict(source=str(src), output=str(work / 'auto.png'), settings={}), work)['events'][-1]
print('Automatik (Rezept):', size(auto['result']['image']), '| preparation:', auto['result']['analysis']['preparation']['corners'], 'rotate', auto['result']['analysis']['preparation']['rotate'])

# (a) Swift nach openMask ohne Plan + "Uebernehmen": corners=Vollbild, rotation=nil, use_saved_retouches=false
full = dict(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], use_saved_retouches=False)
a = bridge(res, 'preview', dict(source=str(src), output=str(work / 'a.png'), settings=full), work)['events'][-1]
pa = Image.open(a['result']['image']).convert('RGB'); arr = np.array(pa)
tisch = (np.abs(arr.astype(int) - [150, 100, 60]).sum(axis=2) < 60).mean()
print('(a) Nach Uebernehmen ohne Aenderung:', pa.size, '| Anteil Tischfarbe im Ergebnis: %.1f %%' % (100 * tisch),
      '| preparation.corners:', a['result']['analysis']['preparation']['corners'])

# (b) Nutzer zieht die Ecken korrekt, rotation bleibt nil; Maskenbild vs. Render
user = dict(corners=corners, use_saved_retouches=False)
m = bridge(res, 'prepare', dict(source=str(src), output=str(work / 'mask.png'), settings=user), work)['events'][-1]
print('(b) Maskenbild (prepare) Groesse:', size(m['result']['image']), '-> Hochformat, nicht gedreht')
stroke = dict(points=[[0.08, 0.06], [0.2, 0.06], [0.2, 0.12], [0.08, 0.12]], radius=0.05)  # oben links im Maskenbild
r0 = bridge(res, 'preview', dict(source=str(src), output=str(work / 'b0.png'), settings=user), work)['events'][-1]
r1 = bridge(res, 'preview', dict(source=str(src), output=str(work / 'b1.png'), settings=dict(user, retouch_strokes=[stroke])), work)['events'][-1]
b0 = np.array(Image.open(r0['result']['image']).convert('L'), float); b1 = np.array(Image.open(r1['result']['image']).convert('L'), float)
print('    Render-Groesse:', b0.shape[::-1], '-> Querformat (Rezeptdrehung 90 angewendet)')
ys, xs = np.nonzero(np.abs(b1 - b0) > 25)
cx, cy = xs.mean() / b0.shape[1], ys.mean() / b0.shape[0]
# Wo liegt die im Maskenbild markierte Stelle (x=0.14,y=0.09) nach rotate(90, expand) gegen den Uhrzeigersinn?
print('    Retusche wirkt im Ergebnis bei (x=%.2f, y=%.2f); beabsichtigt waere (x=%.2f, y=%.2f)' % (cx, cy, 0.09, 1 - 0.14))
