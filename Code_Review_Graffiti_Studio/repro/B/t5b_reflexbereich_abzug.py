"""Ergaenzung zu Hinweis 5: Auf einem Abzug mit automatischer Reflexminderung (Rezept glare_strength .62 -> Regler Auto=70)
schaltet ein kleines Reflexrechteck die Minderung ausserhalb des Rechtecks ab. Ausserdem: Drehung im Inspector
(ohne Editor) bei einem Foto mit schwarzen Balken."""
import sys, pathlib, copy
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image
from adjustments import Settings
from analysis import apply_plan
rng = np.random.default_rng(2)
a = rng.integers(20, 120, (900, 1200, 3)).astype(np.float32) * 0.5 + 90  # gleichmaessiger Schleier ueber dem ganzen Abzug
img = Image.fromarray(a.astype(np.uint8))
plan = dict(preparation=dict(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], rotate=0, glare_strength=.62), look='kraeftig', features={}, warnings=[], white_balance_rgb=[1, 1, 1])
def run(s):
    p, c = s.prepare_plan(plan); return np.array(apply_plan(img, p)[0]).astype(int), c
base = np.array(img).astype(int)
auto, c = run(Settings(corners=plan['preparation']['corners'], rotation=0))
reg, c2 = run(Settings(corners=plan['preparation']['corners'], rotation=0, glare_regions=[[0.05, 0.05, 0.2, 0.2]]))
out = np.ones(base.shape[:2], bool); out[0:270, 0:360] = False  # weit ausserhalb des Rechtecks (inkl. Weichzeichnungsrand)
print('Regler glare (Auto) =', c['glare'], '| mittlere Helligkeit ausserhalb des Rechtecks: Original', round(base[out].mean(), 1),
      '| ohne Rechteck', round(auto[out].mean(), 1), '| mit kleinem Rechteck', round(reg[out].mean(), 1))
# Inspector-Drehung bei Panorama mit schwarzen Balken (border_crop), ohne Masken-Editor
pano = np.full((700, 2400, 3), 120, np.uint8); pano[:80] = 0; pano[-80:] = 0
plan2 = dict(preparation=None, border_crop=[0, 80, 2400, 620], look='kraeftig', features={}, warnings=[], white_balance_rgb=[1, 1, 1])
for label, s in [('Drehung Automatisch', Settings()), ('Drehung 0° im Inspector', Settings(rotation=0)), ('Drehung 180° im Inspector', Settings(rotation=180))]:
    p, _ = s.prepare_plan(plan2); o = np.array(apply_plan(Image.fromarray(pano), p)[0])
    print(f'{label:26s}: Ausgabe {o.shape[1]}x{o.shape[0]}, schwarze Zeilen {(o.max(axis=(1, 2)) == 0).sum()}')
