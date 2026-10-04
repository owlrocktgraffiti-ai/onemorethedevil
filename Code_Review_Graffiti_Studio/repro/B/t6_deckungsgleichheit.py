"""Hinweis 6: Deckungsgleichheit Maskenbild (prepare: thumbnail 1800 -> transform) vs. Export (Vollaufloesung -> transform).
Misst die Lage eines Markers und einer normierten Region in beiden Bildern (in Export-Pixeln)."""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np, cv2
from PIL import Image, ImageDraw
from photo_prepare import transform

def centroid(a):
    m = (a[:, :, 0] > 200) & (a[:, :, 1] < 60) & (a[:, :, 2] < 60); ys, xs = np.nonzero(m)
    return np.array([xs.mean() / a.shape[1], ys.mean() / a.shape[0]])

worst = 0
for (W, H) in [(4032, 3024), (3024, 4032), (5000, 1234), (1999, 1801), (7000, 3000)]:
    im = Image.new('RGB', (W, H), (90, 90, 90)); d = ImageDraw.Draw(im)
    pts = [(0.37 * W, 0.41 * H), (0.70 * W, 0.66 * H), (0.15 * W, 0.80 * H)]
    for x, y in pts: d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 0, 0))
    corners = [[0.07, 0.05], [0.93, 0.09], [0.88, 0.95], [0.11, 0.91]]
    for rot in (0, 90):
        small = im.copy(); small.thumbnail((1800, 1800))
        cfg = dict(corners=corners, rotate=rot, glare_strength=0)
        a_s = transform(small, cfg); a_f = transform(im, cfg)
        # Marker einzeln vergleichen
        dev = []
        for x, y in pts:
            one = Image.new('RGB', (W, H), (90, 90, 90)); ImageDraw.Draw(one).ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 0, 0))
            s1 = one.copy(); s1.thumbnail((1800, 1800))
            cs = centroid(np.array(transform(s1, cfg))); cf = centroid(np.array(transform(one, cfg)))
            dev.append(np.abs((cs - cf) * [a_f.width, a_f.height]).max())
        # Seitenverhaeltnis
        ar = abs(a_s.width / a_s.height - a_f.width / a_f.height) / (a_f.width / a_f.height)
        # Region: Swift zeichnet [x0*rw, x1*rw], Python schneidet int(x0*W):int(x1*W)
        x0, y0, x1, y1 = 0.3333, 0.25551, 0.6667, 0.7449
        Wf, Hf = a_f.size
        py = (int(x0 * Wf), int(y0 * Hf), int(x1 * Wf), int(y1 * Hf))
        sw = (x0 * Wf, y0 * Hf, x1 * Wf, y1 * Hf)
        rdev = max(abs(p - s) for p, s in zip(py, sw))
        worst = max(worst, max(dev), rdev)
        print(f'{W}x{H} rot={rot}: Maskenbild {a_s.size} Export {a_f.size}; Markerabweichung (Export-px) max {max(dev):.2f}; '
              f'Seitenverhaeltnis-Abw. {ar*100:.3f} %; Regionskante int() vs. Swift {rdev:.2f} px')
print('groesste Abweichung in Export-Pixeln:', round(float(worst), 2))
