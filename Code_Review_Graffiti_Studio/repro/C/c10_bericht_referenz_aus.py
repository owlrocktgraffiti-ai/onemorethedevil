"""C10: Bericht/Plan bei abgeschalteter oder durch Maske verdraengter Referenzretusche.
analysis.analyze haengt bei bekanntem Fingerabdruck die Warnung 'Die hinterlegte Einzelretusche enthaelt KI-rekonstruierte
Details.' an und UNTERDRUECKT die Blitz-/Clipping-Warnungen (analysis.py:117-118,142-148). adjustments.prepare_plan entfernt
danach cached_correction (adjustments.py:91,96), laesst aber die Warnungen stehen."""
from common import *
from PIL import Image
import numpy as np, re
work, res = fresh('c10')
sys.path.insert(0, str(res))
from analysis import digest_image
from graffiti import read_image
rng = np.random.default_rng(10)
a = np.clip(np.array(Image.fromarray(rng.integers(40, 160, (60, 80, 3), dtype=np.uint8)).resize((800, 600), Image.BICUBIC)).astype(int), 0, 255).astype(np.uint8)
yy, xx = np.mgrid[:600, :800]; a[((xx - 400) ** 2 + (yy - 300) ** 2) < 45 ** 2] = 255      # zentraler ausgebrannter Blitzfleck
p = work / 'Blitz.jpg'; Image.fromarray(a).save(p, quality=95)
(res / 'Referenzkorrekturen').mkdir(exist_ok=True); cached = res / 'Referenzkorrekturen/K.png'; Image.fromarray(a).save(cached)
known = json.loads((res / 'Bekannte_Retuschen.json').read_text())
known.append(dict(source_name='Blitz.jpg', image_sha256=digest_image(read_image(p)), cached='Referenzkorrekturen/K.png', cached_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(), description='Test', generative_reconstruction=True))
(res / 'Bekannte_Retuschen.json').write_text(json.dumps(known))
for tag, k in [('Referenz an (Standard)', knob(mode='klassisch', scale=1)),
               ('Schalter "Bekannte Einzelretuschen" aus', knob(mode='klassisch', scale=1, references=False)),
               ('Retuschpinsel-Strich gesetzt (closeMask)', knob(mode='klassisch', scale=1, references=False, corners=[[0, 0], [1, 0], [1, 1], [0, 1]], strokes=[dict(points=[[0.1, 0.1]], radius=0.02)]))]:
    out = work / ('Ordner_' + str(time.time_ns()))
    f = final(bridge(res, 'batch', swift_export_library([str(p)], str(p), k, {}, out), work))
    plan = json.loads((out / '01_Blitz.json').read_text())
    html = (out / 'Pruefbericht.html').read_text()
    print(f'--- {tag}: cached_correction im Plan: {"cached_correction" in plan}')
    print('    executed:', [x for x in plan['executed'] if 'Retusche' in x or 'Rekonstruktion' in x] or '(keine Referenz ausgefuehrt)')
    print('    warnings:', plan['warnings'])
    print('    Bericht nennt KI-Rekonstruktion:', 'KI-rekonstruierte' in html, '| Bericht nennt Blitz:', 'Kamerablitz' in html)
# Gegenprobe: dasselbe Bild ohne Referenzeintrag
work2, res2 = fresh('c10b')
out = work2 / 'Ordner_x'
f = final(bridge(res2, 'batch', swift_export_library([str(p)], str(p), knob(mode='klassisch', scale=1), {}, out), work2))
print('--- Gegenprobe ohne Referenzeintrag: warnings:', json.loads((out / '01_Blitz.json').read_text())['warnings'])
