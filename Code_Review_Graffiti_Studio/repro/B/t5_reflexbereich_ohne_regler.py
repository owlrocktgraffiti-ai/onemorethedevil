"""Hinweis 5: Reflexrechtecke auf Nicht-Abzuegen wirken nicht, solange der Reflexregler auf 0 (Auto) steht.
Vollstaendiger Weg wie in der App: read_image -> analyze -> Settings.prepare_plan -> apply_plan (transform)."""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from adjustments import Settings
from analysis import analyze, apply_plan

work = HERE / 'out_t5'; work.mkdir(exist_ok=True)
# Wandfoto (kein Abzug) mit grauem Reflexschleier rechts oben
rng = np.random.default_rng(1)
a = rng.integers(20, 120, (900, 1200, 3)).astype(np.float32)
a[100:400, 700:1100] = a[100:400, 700:1100] * 0.4 + 150  # additiver Schleier
src = work / 'wand.png'; Image.fromarray(a.astype(np.uint8)).save(src)
img = Image.open(src).convert('RGB')
plan = analyze(img, src, ocr=False)
print('Analyse: preparation =', plan['preparation'], '| border_crop =', plan.get('border_crop'))
region = [700 / 1200, 100 / 900, 1100 / 1200, 400 / 900]
full = [[0, 0], [1, 0], [1, 1], [0, 1]]

def run(settings):
    p, controls = settings.prepare_plan(plan)
    out, notes = apply_plan(img, p)
    return np.array(out).astype(int), p, controls

ref, _, _ = run(Settings(corners=full))
for label, s in [('Reflexbereich gezeichnet, Regler Auto', Settings(corners=full, glare_regions=[region])),
                 ('Reflexbereich gezeichnet, Regler 50 %', Settings(corners=full, glare_regions=[region], values=dict(glare=50)))]:
    out, p, controls = run(s)
    y0, y1, x0, x1 = 100, 400, 700, 1100
    inside = np.abs(out[y0:y1, x0:x1] - ref[y0:y1, x0:x1]).mean()
    print(f'{label:40s}: controls.glare={controls["glare"]:3d} preparation.glare_strength={p["preparation"]["glare_strength"]:.3f} '
          f'mittlere Aenderung im Rechteck={inside:.2f} | Warnungen zur Reflexmaske: {[w for w in p["warnings"] if "Reflex" in w]}')
