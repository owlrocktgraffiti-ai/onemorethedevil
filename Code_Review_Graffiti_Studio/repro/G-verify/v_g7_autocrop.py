"""G7: unbekanntes Zugfoto (kein Abzug) vor warmem Hintergrund, App-Standardeinstellungen (KnobState() aus Swift) ueber native_bridge preview."""
import json
import numpy as np
from PIL import Image, ImageDraw
from vcommon import *
res = fresh_resources('g7'); inp = res.parent / 'in'; inp.mkdir()
default = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])
rng = np.random.default_rng(11)
a = np.clip(np.full((1000, 1500, 3), (175, 105, 65), int) + rng.integers(-10, 11, (1000, 1500, 1)), 0, 255).astype(np.uint8)
im = Image.fromarray(a); d = ImageDraw.Draw(im)
d.rectangle((60, 120, 1440, 820), fill=(195, 198, 205))
for i in range(6):
    cx = 120 + i*210; d.ellipse((cx, 200, cx+170, 730), fill=[(230, 40, 40), (250, 200, 30), (40, 160, 230)][i % 3])
src = inp / 'zug_backstein.jpg'; im.save(src, quality=95)
for label, s in [('Standard', default), ('Papierkanten aus', dict(default, geometry='aus'))]:
    code, ev, err = bridge(res, 'preview', dict(source=str(src), output=str(res.parent / (label + '.png')), settings=s))
    out = ev[-1]['result']; plan = out['analysis']; prep = plan.get('preparation') or {}
    print(f'{label}: Original 1500x1000 -> Vorschau {Image.open(out["image"]).size} | paper_confidence={plan.get("paper_confidence")} | '
          f'corners={prep.get("corners")} glare_strength={prep.get("glare_strength")} | executed[0]={plan["executed"][0][:40]!r} | '
          f'Papierkanten-Aktion={[x for x in plan["actions"] if "Papierkanten" in x]} | Warnungen={[w for w in plan["warnings"] if "KI" not in w]}')
