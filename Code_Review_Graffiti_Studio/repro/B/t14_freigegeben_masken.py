"""Freigegebenes Bild (Freigegebene_Bilder.json): Ecken/Masken aus dem Editor werden ohne Hinweis ignoriert."""
import sys, json, hashlib, pathlib, shutil
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / 'Resources_t14'
shutil.rmtree(RES, ignore_errors=True); shutil.copytree(HERE / 'Resources', RES)
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image
work = HERE / 'out_t14'; work.mkdir(exist_ok=True)
src = work / 'freigegeben.jpg'; Image.new('RGB', (1200, 800), (150, 120, 90)).save(src, quality=95)
from graffiti import read_image
d = hashlib.sha256(read_image(src).tobytes()).hexdigest()
(RES / 'Freigegebene_Bilder.json').write_text(json.dumps([dict(image_sha256=d, description='Test')]))
import graffiti
from studio_backend import render_one
from adjustments import Settings
graffiti.SESSION.update(ai_available=False, ocr_available=False)
s = Settings(corners=[[0.2, 0.2], [0.8, 0.2], [0.8, 0.8], [0.2, 0.8]], rotation=90, retouch_strokes=[dict(points=[[.5, .5]], radius=.05)], glare_regions=[[.1, .1, .4, .4]], values=dict(glare=50, exposure=100))
r = render_one(src, work / 'out.png', s, False)
print('Ausgabe:', r['image'], Image.open(r['image']).size, '| identisch mit Quelle:', pathlib.Path(r['image']).read_bytes() == src.read_bytes())
print('Warnungen:', r['analysis']['warnings'], '| executed:', r['analysis']['executed'])
