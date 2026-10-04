"""A5: exportLibrary() (GraffitiStudio.swift:147-150) nimmt geometry und use_saved_retouches immer aus den
Knobs des GERADE AUSGEWAEHLTEN Fotos (base); merged uebernimmt saved.geometry nie und references nur,
wenn es false ist. closeMask() setzt references=false. Simuliert wird der Request, den Swift schickt, wenn
das ausgewaehlte Foto "Automatische Papierkanten" aus hat bzw. im Masken-Editor bearbeitet wurde.
Foto 1: Abzug mit hinterlegtem Rezept (wie IMG_4363, rotate 90). Foto 2: Foto mit bekannter Referenzretusche.
"""
from common import *
from PIL import Image
import numpy as np, hashlib, sys
work, res = fresh_resources('r5')
sys.path.insert(0, str(res))
from analysis import digest_image
from graffiti import read_image
rng = np.random.default_rng(5)
W, H = 900, 1200
img = np.zeros((H, W, 3), np.uint8); img[:] = (150, 100, 60)
img[60:H - 84, 45:W - 135] = np.array(Image.fromarray(rng.integers(0, 255, (60, 45, 3), dtype=np.uint8)).resize((W - 180, H - 144), Image.BICUBIC))
p1 = work / 'Abzug.jpg'; Image.fromarray(img).save(p1, quality=95)
rec = json.loads((res / 'Fotorezepte.json').read_text())
rec['Abzug.jpg'] = dict(corners=[[0.05, 0.05], [0.85, 0.05], [0.85, 0.93], [0.05, 0.93]], rotate=90, glare_strength=0.62, source_size=[W, H], image_sha256=digest_image(read_image(p1)))
(res / 'Fotorezepte.json').write_text(json.dumps(rec, indent=2))
p2 = work / 'Wand.png'; Image.fromarray(rng.integers(0, 255, (300, 400, 3), dtype=np.uint8)).save(p2)
(res / 'Referenzkorrekturen').mkdir(exist_ok=True)
cached = res / 'Referenzkorrekturen/Test.png'; Image.new('RGB', (400, 300), (0, 200, 0)).save(cached)
known = json.loads((res / 'Bekannte_Retuschen.json').read_text())
known.append(dict(source_name='Wand.png', image_sha256=digest_image(read_image(p2)), cached='Referenzkorrekturen/Test.png',
                  cached_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(), description='Test', generative_reconstruction=True))
(res / 'Bekannte_Retuschen.json').write_text(json.dumps(known, indent=2))

def batch(base, tag):
    # Swift: per_photo enthaelt besuchte Fotos als merged=base+saved (geometry/references aus base)
    per = {str(p1): base, str(p2): base}
    ev = bridge(res, 'batch', dict(files=[str(p1), str(p2)], output=str(work / tag), settings=base, per_photo=per), work)['events'][-1]
    out = work / tag
    a = Image.open(out / '01_Abzug.png'); b = np.array(Image.open(out / '02_Wand.png').convert('RGB')).astype(int)
    green = ((b[:, :, 1] > 150) & (b[:, :, 0] < 80)).mean()
    print(f'{tag:34s} Abzug: {a.size} ({"Hochformat, ungedreht" if a.height > a.width else "Querformat, gedreht"}) | Referenzretusche angewendet: {green > .9}')

batch({}, 'korrekt (Basis=Automatik)')
batch(dict(geometry='aus'), 'Basis: Papierkanten aus')
batch(dict(use_saved_retouches=False), 'Basis: nach closeMask')
