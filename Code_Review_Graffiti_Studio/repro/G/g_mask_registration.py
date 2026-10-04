"""Regressionstest-Vorschlag 'Masken nach Drehung/Perspektive': Ein Pinselstrich/Reflexrechteck, das auf dem
'prepare'-Bild (Maskeneditor, Swift:312 maskImage) bei normierten Koordinaten P gesetzt wird, muss in der
Vorschau/dem Export an derselben normierten Stelle wirken. Gemessen ueber Differenzbild mit/ohne Maske."""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np
from PIL import Image, ImageDraw
res = fresh_resources('maskreg'); wd = res.parent
# Foto mit EXIF-Orientierung 6 (wie iPhone hochkant) und Textur
rng = np.random.default_rng(4)
base = rng.integers(40, 200, (900, 1300, 3), dtype=np.uint8)
for y in range(0, 900, 60): base[y:y + 6] = 250
img = Image.fromarray(base)
exif = Image.Exif(); exif[0x0112] = 6
img.save(wd / 'foto.jpg', quality=95, exif=exif.tobytes())   # Anzeige: 900x1300 hochkant
corners = [[0.10, 0.08], [0.88, 0.12], [0.93, 0.90], [0.05, 0.95]]
ok_all = True
for rot in (0, 90, 180, 270):
    common = dict(mode='klassisch', scale=1, corners=corners, rotation=rot, values=dict(retouch_strength=100, glare=100))
    code, ev, err = bridge(res, 'prepare', dict(source=str(wd / 'foto.jpg'), output=str(wd / f'prep{rot}.png'), settings=common), wd)
    prep = Image.open(ev[-1]['result']['image']); pw, ph = prep.size
    for kind, extra, target in [('Pinsel', dict(retouch_strokes=[dict(points=[[0.30, 0.65], [0.36, 0.65]], radius=0.04)]), (0.33, 0.65)),
                                ('Reflexrechteck', dict(glare_regions=[[0.60, 0.15, 0.80, 0.35]]), (0.70, 0.25))]:
        outs = []
        for with_mask in (False, True):
            # Pinsel: ohne/mit Strich. Reflexrechteck: Rechteck immer gesetzt, Regler 0 % gegen 100 %
            if kind == 'Pinsel': s = dict(common, **(extra if with_mask else {}))
            else: s = dict(common, **extra, values=dict(retouch_strength=100, glare=100 if with_mask else 0))
            code, ev, err = bridge(res, 'export', dict(source=str(wd / 'foto.jpg'), output=str(wd / f'E{rot}{kind}{with_mask}' / 'r.png'), settings=s), wd)
            if ev[-1]['type'] != 'result': print('FEHLER', ev[-1]); sys.exit(1)
            outs.append(np.asarray(Image.open(ev[-1]['result']['image']).convert('L')).astype(int))
        a, b = outs; h, w = a.shape
        diff = np.abs(a - b) > 12
        ys, xs = np.nonzero(diff)
        c = (xs.mean() / w, ys.mean() / h) if len(xs) else (float('nan'), float('nan'))
        err_px = max(abs(c[0] - target[0]), abs(c[1] - target[1]))
        ok = err_px < 0.03 and abs(pw / ph - w / h) < 0.01
        ok_all &= ok
        print(f'Drehung {rot:3}° {kind:15} prepare {pw}x{ph} (Seitenv. {pw/ph:.3f}) export {w}x{h} (Seitenv. {w/h:.3f}) '
              f'Ziel {target} Wirkungsschwerpunkt ({c[0]:.3f},{c[1]:.3f}) -> {"OK" if ok else "ABWEICHUNG"}')
print('GESAMT', 'OK' if ok_all else 'ABWEICHUNG')
