"""A12: Ein im Masken-Editor gezogener "Reflexbereich" wirkt nur, wenn der Regler "Reflexschleier" > 0 ist.
Bei Fotos ohne erkannten Abzug steht dieser auf Auto = 0 % -> der markierte Bereich bleibt wirkungslos,
ohne Hinweis (adjustments.py:86,104-107; Warnung nur im umgekehrten Fall).
Zusaetzlich: Plan-JSONs der Vorschau (render_one schreibt <ziel>.json) bleiben liegen, clearOldPreviews
loescht nur .png (GraffitiStudio.swift:140).
"""
from common import *
from PIL import Image
import numpy as np, uuid
work, res = fresh_resources('r8')
src = work / 'wand.png'
a = np.random.default_rng(8).integers(0, 120, (600, 800, 3), dtype=np.uint8); a[200:400, 250:550] += 120   # heller "Schleier"
Image.fromarray(a).save(src)
temp = work / 'GraffitiStudio-temp'; temp.mkdir()
def prev(settings):
    target = temp / (str(uuid.uuid4()).upper() + '.png')
    ev = bridge(res, 'preview', dict(source=str(src), output=str(target), settings=settings), work)['events'][-1]
    return np.array(Image.open(ev['result']['image']).convert('RGB')).astype(int), ev['result']['analysis']
full = [[0, 0], [1, 0], [1, 1], [0, 1]]
base, _ = prev(dict(corners=full, use_saved_retouches=False))
reg, plan = prev(dict(corners=full, use_saved_retouches=False, glare_regions=[[0.3, 0.3, 0.7, 0.7]]))
reg50, _ = prev(dict(corners=full, use_saved_retouches=False, glare_regions=[[0.3, 0.3, 0.7, 0.7]], values=dict(glare=50)))
print('Reflexbereich, Regler Auto: controls.glare =', plan['controls']['glare'], '| max. Pixelabweichung zu ohne Bereich =', int(np.abs(reg - base).max()), '| Warnungen:', plan['warnings'])
print('Reflexbereich, Regler 50 %: max. Pixelabweichung =', int(np.abs(reg50 - base).max()))
# Swift-clearOldPreviews nachgebildet: nur .png ausser der aktuellen loeschen
keep = sorted(temp.glob('*.png'))[-1]
for p in temp.glob('*.png'):
    if p != keep: p.unlink()
print('Temp-Ordner nach 3 Vorschauen + clearOldPreviews:', sorted(x.suffix for x in temp.iterdir()), '| Groesse Plan-JSON je Vorschau ~', max(x.stat().st_size for x in temp.glob('*.json')), 'Byte')
