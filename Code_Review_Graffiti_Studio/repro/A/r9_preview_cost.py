"""A13: Jede Reglerbewegung startet nach 0,32 s einen NEUEN Python-Prozess, der Bibliotheken importiert, das
12-MP-Original dekodiert und die komplette Analyse (inkl. OCR, falls vorhanden, bis 45 s) wiederholt.
Gemessen: zwei Vorschauen desselben Fotos, die sich nur in contrast=10 vs. 20 unterscheiden.
"""
from common import *
from PIL import Image
import numpy as np
work, res = fresh_resources('r9')
rng = np.random.default_rng(9)
img = Image.fromarray(rng.integers(0, 255, (189, 252, 3), dtype=np.uint8)).resize((4032, 3024), Image.BICUBIC)
src = work / 'IMG_12MP.jpg'; img.save(src, quality=92)
t0 = time.monotonic(); subprocess.run([PY, '-c', 'import sys;sys.path.insert(0,%r);import native_bridge' % str(res)], check=True); imp = time.monotonic() - t0
for v in (10, 20):
    r = bridge(res, 'preview', dict(source=str(src), output=str(work / f'c{v}.png'), settings=dict(mode='klassisch', values=dict(contrast=v))), work)
    stages = [e.get('stage') for e in r['events'] if e['type'] == 'progress']
    print(f'contrast={v}: Vorschau-Prozess {r["seconds"]} s (davon Interpreter+Importe ~{imp:.2f} s), Stufen {stages}')
