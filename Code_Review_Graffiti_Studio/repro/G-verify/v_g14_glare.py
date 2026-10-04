"""G14: Reflexrechteck auf normalem Foto bei Regler 'Auto' (values ohne glare)."""
import json
import numpy as np
from PIL import Image
from vcommon import *
res = fresh_resources('g14'); inp = res.parent / 'in'; inp.mkdir()
rng = np.random.default_rng(4)
a = rng.integers(40, 160, (600, 900, 3)).astype(np.float32); a[150:450, 300:600] = a[150:450, 300:600]*.5 + 110  # Schleier
src = inp / 'foto.png'; Image.fromarray(a.astype(np.uint8)).save(src)
base = dict(mode='klassisch', values={})
def run(tag, s):
    code, ev, err = bridge(res, 'preview', dict(source=str(src), output=str(res.parent / f'{tag}.png'), settings=s))
    r = ev[-1]['result']; return np.array(Image.open(r['image'])).astype(int), r['analysis']
ref, _ = run('ohne', base)
x, plan = run('auto', dict(base, glare_regions=[[.3, .2, .7, .8]]))
d = np.abs(x - ref)
print(f'Rechteck, Regler Auto: controls.glare={plan["controls"]["glare"]} preparation.glare_strength={plan["preparation"]["glare_strength"]} | Diff zu ohne Rechteck: max {d.max()} Anteil>5: {(d.max(axis=2) > 5).mean():.3f} | Hinweis im Plan: {[w for w in plan["warnings"] if "Reflex" in w]}')
y, plan = run('70', dict(base, glare_regions=[[.3, .2, .7, .8]], values={'glare': 70}))
d = np.abs(y - ref)
print(f'Rechteck, Regler 70 %: Diff max {d.max()} Anteil>5: {(d.max(axis=2) > 5).mean():.3f}')
