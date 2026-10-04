"""D6: Reflexschleier (photo_prepare.transform) – Regionsmaske, globale Wirkung, Auto-Wert."""
import numpy as np, cv2
from PIL import Image
import common
from photo_prepare import transform
from adjustments import Settings
from graffiti import process

OUT = common.OUT / 't6'; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(6)
W, H = 4032, 3024
scene = np.zeros((H, W, 3), np.float32)
scene[:] = (90, 60, 40)
for i in range(400):
    x, y = rng.integers(0, W), rng.integers(0, H)
    cv2.circle(scene, (int(x), int(y)), int(rng.integers(10, 80)), tuple(float(c) for c in rng.integers(0, 200, 3)), -1)
scene += rng.normal(0, 4, scene.shape)
# Additiver neutraler Reflexschleier (+70) in einem kleinen, vom Nutzer markierten Rechteck 3 % x 3 %
rx0, ry0, rx1, ry1 = 0.50, 0.50, 0.53, 0.53
X0, Y0, X1, Y1 = int(rx0 * W), int(ry0 * H), int(rx1 * W), int(ry1 * H)
veiled = scene.copy(); veiled[Y0:Y1, X0:X1] = veiled[Y0:Y1, X0:X1] * (1 - 70 / 255) + 70
img = Image.fromarray(np.clip(veiled, 0, 255).astype(np.uint8))
full = dict(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], rotate=0, glare_strength=.85)
o_none = np.array(transform(img, dict(full, glare_strength=0))).astype(float)
o_global = np.array(transform(img, full)).astype(float)
o_region = np.array(transform(img, dict(full, glare_regions=[[rx0, ry0, rx1, ry1]]))).astype(float)
inside = (slice(Y0 + 5, Y1 - 5), slice(X0 + 5, X1 - 5))
ring = np.zeros((H, W), bool); ring[Y0 - 150:Y1 + 150, X0 - 150:X1 + 150] = True; ring[Y0 - 30:Y1 + 30, X0 - 30:X1 + 30] = False
eff_g = (o_none - o_global)[inside].mean(); eff_r = (o_none - o_region)[inside].mean()
print(f'Region {X1-X0}x{Y1-Y0} px. Mittlere Abdunklung im markierten Rechteck: ohne Region (Maske=1) {eff_g:.1f}, mit Region {eff_r:.1f} '
      f'-> {100*eff_r/eff_g:.0f} % der Sollwirkung')
print(f'Rest-Schleier im Rechteck: Szene {scene[inside].mean():.1f}, Eingabe {veiled[inside].mean():.1f}, Ausgabe Region {o_region[inside].mean():.1f}')
print(f'Wirkung AUSSERHALB (30..150 px Abstand): mittlere Abdunklung {(o_none - o_region)[ring].mean():.1f}, max {(o_none - o_region)[ring].max():.0f}')
# Maskenmaximum direkt nachrechnen (wie transform Zeile 56-59)
m = np.zeros((H, W), np.float32); m[Y0:Y1, X0:X1] = 1; m = cv2.GaussianBlur(m, (0, 0), max(4, min(H, W) * .02))
print(f'Maske nach GaussianBlur(sigma={max(4, min(H, W)*.02):.0f}): Maximum {m.max():.2f}, an der Rechteckkante {m[Y0, (X0+X1)//2]:.2f}, 100 px außerhalb {m[Y0-100, (X0+X1)//2]:.2f}')
for frac in (0.03, 0.06, 0.10, 0.20):
    m = np.zeros((H, W), np.float32); y0, x0 = int(.4 * H), int(.4 * W); m[y0:y0 + int(frac * H), x0:x0 + int(frac * W)] = 1
    m = cv2.GaussianBlur(m, (0, 0), max(4, min(H, W) * .02)); print(f'   Rechteck {int(frac*100)} %: Maskenmaximum {m.max():.2f}')

# Globale Wirkung nur durch Drehung 0° (kein Abzug, kein Bereich) – Wandfoto
wall = OUT / 'wall.png'; Image.fromarray(np.clip(scene + 40, 0, 255).astype(np.uint8)).resize((2016, 1512)).save(wall)
r1, p1 = process(wall, OUT / 'a.png', 'klassisch', 1, 'auto', 'auto', None, Settings(mode='klassisch', scale=1, values={'glare': 50}))
r2, p2 = process(wall, OUT / 'b.png', 'klassisch', 1, 'auto', 'auto', None, Settings(mode='klassisch', scale=1, rotation=0, values={'glare': 50}))
d = np.abs(np.array(r1).astype(float) - np.array(r2).astype(float))
print(f'glare=50 ohne Drehung: Mittel {np.array(r1).mean():.1f}; Warnung: {[w for w in p1["warnings"] if "Reflex" in w]}')
print(f'glare=50 + Drehung 0°: Mittel {np.array(r2).mean():.1f}; mittlere |Diff| {d.mean():.1f}; Warnungen Reflex: {[w for w in p2["warnings"] if "Reflex" in w]}')
# Reflexbereich markiert, Regler auf Auto -> Wirkung?
r3, p3 = process(wall, OUT / 'c.png', 'klassisch', 1, 'auto', 'auto', None, Settings(mode='klassisch', scale=1, glare_regions=[[.3, .3, .6, .6]]))
r4, p4 = process(wall, OUT / 'd.png', 'klassisch', 1, 'auto', 'auto', None, Settings(mode='klassisch', scale=1))
print(f'Reflexbereich markiert, Regler Auto: controls.glare={p3["controls"]["glare"]}, glare_strength={p3["preparation"]["glare_strength"]}, '
      f'max |Diff| zu ohne Bereich = {np.abs(np.array(r3).astype(int) - np.array(r4).astype(int)).max()}, Warnungen: {[w for w in p3["warnings"] if "Reflex" in w]}')
