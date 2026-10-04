"""D3: Vorschau (1440x1000) vs. Export (1x/2x), verglichen nach Verkleinerung des Exports auf Vorschaugröße.
render() läuft nach dem Skalieren; Median 3 px, Unschärfemaske 0,8 px und Bilateral d=5 sind feste Pixelmaße."""
import numpy as np, cv2, time
from PIL import Image
import common
from adjustments import Settings, CONTROL_SPEC
from graffiti import process

OUT = common.OUT / 't3'; OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(3)
W, H = 4032, 3024
base = np.full((H, W, 3), (150, 140, 130), np.float32)
# Schrift-/Outline-artige Struktur: dünne dunkle Linien, Buchstaben, Flächen
img = base.copy()
for i in range(60):
    x = int(rng.integers(0, W - 400)); y = int(rng.integers(60, H - 60))
    cv2.putText(img, 'GRAFFITI', (x, y), cv2.FONT_HERSHEY_SIMPLEX, float(rng.uniform(1.5, 4)),
                tuple(float(c) for c in rng.integers(0, 255, 3)), int(rng.integers(2, 7)), cv2.LINE_AA)
img[200:900, 200:1400] = (150, 140, 130)  # flache Prüffläche
img += rng.normal(0, 9, img.shape)  # Sensorrauschen
src = OUT / 'test.png'
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(src)

zero = {k: 0 for k in CONTROL_SPEC}; zero['ki_strength'] = 0


def run(values, preview, scale):
    t = time.time()
    im, plan = process(src, OUT / 'tmp.png', 'klassisch', scale, 'auto', 'auto', None, Settings(mode='klassisch', scale=scale, values=values),
                       (1440, 1000) if preview else None)
    return np.array(im).astype(np.float32), time.time() - t


def down(a, size):
    return np.array(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).resize(size, Image.Resampling.LANCZOS)).astype(np.float32)


def flat_noise(a, sx):  # Std in der flachen Prüffläche (Koordinaten skaliert)
    y0, y1, x0, x1 = [int(v * sx) for v in (300, 800, 300, 1300)]
    return float(a[y0:y1, x0:x1].std(axis=(0, 1)).mean())


def hf(a):
    g = cv2.cvtColor(np.clip(a, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(g, cv2.CV_32F).var())


P0, tp = run(zero, True, 1)
size = (P0.shape[1], P0.shape[0]); sx = P0.shape[1] / W
print(f'Vorschaugröße {size}, Laufzeit Vorschau {tp:.1f}s')
X0 = {s: run(zero, False, s)[0] for s in (1, 2)}
D0 = {s: down(X0[s], size) for s in (1, 2)}
print(f'neutral: Vorschau Rauschen={flat_noise(P0, sx):.2f} HF={hf(P0):.0f} | Export1x↓ Rauschen={flat_noise(D0[1], sx):.2f} HF={hf(D0[1]):.0f} | Export2x↓ Rauschen={flat_noise(D0[2], sx):.2f} HF={hf(D0[2]):.0f}')
for key in ('denoise', 'sharpness', 'compression'):
    v = dict(zero); v[key] = 100
    P, _ = run(v, True, 1)
    line = f'{key}=100: Vorschau Δ={np.abs(P - P0).mean():.2f} Rauschen={flat_noise(P, sx):.2f} HF={hf(P):.0f}'
    for s in (1, 2):
        X, _ = run(v, False, s); D = down(X, size)
        line += f' | Export{s}x↓ Δ={np.abs(D - D0[s]).mean():.2f} Rauschen={flat_noise(D, sx):.2f} HF={hf(D):.0f}'
    print(line)
# Automatik (Standardwerte der App)
P, _ = run({}, True, 1)
for s in (1, 2):
    X, _ = run({}, False, s); D = down(X, size)
    print(f'Automatik: Export{s}x↓ vs Vorschau: mittlere |Diff|={np.abs(D - P).mean():.2f}, max={np.abs(D - P).max():.0f}; '
          f'Rauschen Vorschau={flat_noise(P, sx):.2f} Export↓={flat_noise(D, sx):.2f}; HF Vorschau={hf(P):.0f} Export↓={hf(D):.0f}')
