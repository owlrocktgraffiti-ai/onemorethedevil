"""D7: Tonkurven nur auf Luma (YCbCr) und Weißabgleich-Verstärkungen auf ausgebrannte Weißflächen."""
import numpy as np, cv2
from PIL import Image
import common
from adjustments import render, CONTROL_SPEC, Settings
from analysis import scan_features, apply_plan

zero = {k: 0 for k in CONTROL_SPEC}


def hsv(px):
    a = np.array([[px]], np.uint8); h, s, v = [int(x) for x in cv2.cvtColor(a, cv2.COLOR_RGB2HSV_FULL)[0, 0]]
    return round(h * 360 / 256), round(s / 255, 2), int(v)


def lab_chroma(px):
    l = cv2.cvtColor(np.array([[px]], np.float32) / 255, cv2.COLOR_RGB2LAB)[0, 0]; return round(float(np.hypot(l[1], l[2])), 1)


def one(px, values):
    v = dict(zero); v.update(values)
    out = render(Image.new('RGB', (64, 64), px), v).getpixel((32, 32)); return out


print('Farbe        Einstellung            Ergebnis         HSV(H,S,V) vorher -> nachher        LAB-Chroma vorher -> nachher   Referenz: RGB-Multiplikation')
for px, vals, ref in [((100, 20, 20), {'exposure': 100}, 4), ((40, 10, 60), {'exposure': 100}, 4), ((60, 25, 10), {'shadows': 70}, None),
                       ((250, 220, 30), {'exposure': -100}, .25), ((30, 120, 220), {'exposure': -100}, .25)]:
    out = one(px, vals)
    refpx = tuple(int(min(255, c * ref)) for c in px) if ref else None
    print(f'{str(px):13s} {str(vals):22s} {str(out):16s} {hsv(px)} -> {hsv(out)}    {lab_chroma(px)} -> {lab_chroma(out)}   '
          + (f'{refpx} HSV {hsv(refpx)}' if refpx else ''))
# Profil "nacht" der Automatik (shadows 70, vibrance 40, denoise 50) auf dunkler gesättigter Farbe
s = Settings(); plan = dict(look='nacht', features={}, preparation=None)
ctrl = s.resolve(plan)
for px in [(70, 15, 15), (15, 30, 70)]:
    out = render(Image.new('RGB', (64, 64), px), ctrl).getpixel((32, 32))
    print(f'Automatik Nacht {px}: -> {out}; HSV-S {hsv(px)[1]} -> {hsv(out)[1]}, LAB-Chroma {lab_chroma(px)} -> {lab_chroma(out)}')

# Weißabgleich: Szene mit warmem Farbstich + ausgebrannter weißer Farbe
rng = np.random.default_rng(7)
a = np.zeros((1000, 1500, 3), np.float32); a[:] = (150, 128, 100)  # graue Wand mit Gelbstich
a[300:700, 400:1100] = 255  # ausgebrannte weiße Farbe/Blitz
a += rng.normal(0, 2, a.shape)
img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
f = scan_features(img)
print('scan_features: cast_suspected', f['cast_suspected'], 'gains', [round(g, 3) for g in f['white_balance_rgb']])
plan = dict(features=f, look='kraeftig', white_balance_rgb=f['white_balance_rgb'], warnings=[], preparation=None)
plan2, controls = Settings().prepare_plan(plan)
print('Automatik-Regler white_balance =', controls['white_balance'], '-> angewandte Verstärkungen', [round(g, 3) for g in plan2['white_balance_rgb']])
out, notes = apply_plan(img, plan2)
o = np.array(out)
print('Ausgebrannte Weißfläche vorher', np.array(img)[500, 700], '-> nach Weißabgleich', o[500:520, 700:720].reshape(-1, 3).mean(0).round(1),
      '; graue Wand', np.array(img)[100:120, 100:120].reshape(-1, 3).mean(0).round(1), '->', o[100:120, 100:120].reshape(-1, 3).mean(0).round(1))
fin = render(out, controls); print('Nach render(Automatik): Weißfläche', np.array(fin)[500:520, 700:720].reshape(-1, 3).mean(0).round(1))

# Stärke der Belichtung: Regler wirkt auf gamma-kodierte Luma (x*2**(e/50)) statt auf lineares Licht
def srgb_to_lin(c): c = c / 255; return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)
def lin_to_srgb(l): l = np.clip(l, 0, 1); return 255 * np.where(l <= .0031308, l * 12.92, 1.055 * l ** (1 / 2.4) - .055)
ramp = Image.fromarray(np.tile(np.arange(256, dtype=np.uint8), (8, 1)).repeat(3).reshape(8, 256, 3))
for e in (50, 100):
    out = np.array(render(ramp, dict(zero, exposure=e)))[4, :, 1].astype(int)
    stops = e / 50
    true = lin_to_srgb(srgb_to_lin(np.arange(256)) * 2 ** stops)
    clip_from = int(np.argmax(out >= 255))
    print(f'Belichtung +{e} % (Doku: +{stops:.0f} Blende): Grau 118 (18 %) -> {out[118]} (echte +{stops:.0f} EV: {true[118]:.0f}); '
          f'Grau 64 -> {out[64]} (echt {true[64]:.0f}); ab Eingangswert {clip_from} reines Weiß (echt ab {int(np.argmax(true >= 254.5))})')
