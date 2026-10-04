"""C2: per_photo-Schluessel. Swift schluesselt mit photo.path (Pfad wie vom Enumerator/NSOpenPanel geliefert,
GraffitiStudio.swift:63,149), Python sucht mit str(source.resolve()) (studio_backend.py:89).
Ordner wird ueber einen Symlink geoeffnet (macOS: /tmp -> /private/tmp, /var -> /private/var, verlinkter Fotoordner).
Engine/realesrgan fehlen -> klassisch."""
from common import *
from PIL import Image
import numpy as np, os
work, res = fresh('c2')
real = work / 'Fotos_echt'; real.mkdir()
rng = np.random.default_rng(2)
Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((1000, 800)).save(real / 'foto.png')
Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((1000, 800)).save(real / 'zweites.png')
link = work / 'Fotos_Link'; os.symlink(real, link)
p1, p2 = str(link / 'foto.png'), str(link / 'zweites.png')
mine = knob(mode='klassisch', scale=1, corners=[[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]], rotation=90, values=dict(exposure=-100),
            strokes=[dict(points=[[0.2, 0.2], [0.8, 0.8]], radius=0.05)])
cur = knob(mode='klassisch', scale=1)
for tag, files, sel in [('Ordner per Symlink geoeffnet (wie Swift)', [p1, p2], p2),
                        ('derselbe Ordner real geoeffnet', [str(real / 'foto.png'), str(real / 'zweites.png')], str(real / 'zweites.png'))]:
    out = work / ('Ordner_' + str(time.time_ns()))
    req = swift_export_library(files, sel, cur, {files[0]: mine}, out)
    r = bridge(res, 'batch', req, work); f = final(r)
    with Image.open(out / '01_foto.png') as im: size = im.size; mean = round(float(np.array(im.convert('L')).mean()), 1)
    plan = json.loads((out / '01_foto.json').read_text())
    print(f'{tag:42s} -> {f["type"]}, 01_foto.png {size} (erwartet mit Nutzer-Ecken+90°: (401, 501)), Helligkeit {mean}, '
          f'settings.corners im Plan: {plan["settings"]["corners"]}, Statusmeldung "Export fertig · {f["result"]["images"]} Bild(er)", warnings={f["result"]["warnings"]}')
print('per_photo-Schluessel:', p1, '| Python-Lookup:', str(Path(p1).resolve()))
