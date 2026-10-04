"""D1: Farbmanagement und Metadaten. JPEG mit Nicht-sRGB-ICC (Display-P3-Primärvalenzen) + EXIF/GPS
wird durch studio_backend.render_one (Pfad der App) geschickt; geprüft wird das Ergebnis-PNG."""
import io, json
import numpy as np
from PIL import Image, ImageCms
import common
from adjustments import Settings, CONTROL_SPEC
from studio_backend import render_one

OUT = common.OUT / 't1'
OUT.mkdir(exist_ok=True)
icc = common.display_p3_like_icc()
rng = np.random.default_rng(1)
W, H = 1600, 1200
a = np.zeros((H, W, 3), np.uint8)
patches = [(220, 40, 40), (40, 200, 60), (50, 70, 210), (240, 200, 30), (128, 128, 128), (250, 120, 180)]
for i, c in enumerate(patches):
    x0 = (i % 3) * (W // 3); y0 = (i // 3) * (H // 2)
    a[y0:y0 + H // 2, x0:x0 + W // 3] = c
a = np.clip(a.astype(int) + rng.normal(0, 6, a.shape), 0, 255).astype(np.uint8)
src_img = Image.fromarray(a)
exif = Image.Exif()
exif[0x010F] = 'Apple'; exif[0x0110] = 'iPhone 13'; exif[0x0132] = '2024:05:01 12:00:00'
exif.get_ifd(0x8769)[0x9003] = '2024:05:01 12:00:00'
gps = exif.get_ifd(0x8825); gps[1] = 'N'; gps[2] = (52.0, 31.0, 12.0); gps[3] = 'E'; gps[4] = (13.0, 24.0, 36.0)
src = OUT / 'p3_exif.jpg'
src_img.save(src, quality=95, icc_profile=icc, exif=exif)
with Image.open(src) as im:
    print('Quelle: icc_profile', len(im.info.get('icc_profile', b'')), 'Bytes; EXIF-Tags', len(im.getexif()),
          'GPS-IFD', dict(im.getexif().get_ifd(0x8825)))


def check(tag, settings):
    dst = OUT / f'{tag}.png'
    r = render_one(src, dst, settings, preview=False)
    with Image.open(r['image']) as im:
        im.load()
        print(f'{tag:28s} icc_profile={len(im.info.get("icc_profile", b"")):4d} B  exif_tags={len(im.getexif())}  '
              f'chunks={sorted(k for k in im.info if k not in ("dpi",))}  backend={r["analysis"]["effective_backend"]}')
        return np.array(im.convert('RGB'))


zero = {k: (0 if CONTROL_SPEC[k][1] <= 0 else 0) for k in CONTROL_SPEC}
zero['ki_strength'] = 0
check('auto_klassisch', Settings(mode='klassisch', scale=1))
neutral = check('alle_regler_0', Settings(mode='klassisch', scale=1, values=zero))
for key, val in [('denoise', 30), ('contrast', 10), ('vibrance', 50), ('sharpness', 50), ('temperature', 20), ('exposure', 10)]:
    v = dict(zero); v[key] = val
    check(f'nur_{key}_{val}', Settings(mode='klassisch', scale=1, values=v))

# Farbwirkung: Pixelwerte im Ergebnis sind P3-Zahlen, werden aber ohne Profil als sRGB angezeigt.
srgb = ImageCms.createProfile('sRGB'); p3 = ImageCms.ImageCmsProfile(io.BytesIO(icc))
t = ImageCms.buildTransform(p3, srgb, 'RGB', 'RGB')
lab = ImageCms.createProfile('LAB')
for i, c in enumerate(patches):
    x0 = (i % 3) * (W // 3) + W // 6; y0 = (i // 3) * (H // 2) + H // 4
    out_px = tuple(int(x) for x in neutral[y0 - 20:y0 + 20, x0 - 20:x0 + 20].reshape(-1, 3).mean(0).round())
    correct = ImageCms.applyTransform(Image.new('RGB', (1, 1), c), t).getpixel((0, 0))
    # Delta E (CIE76) zwischen korrekter sRGB-Darstellung des Originals und der Ergebnis-Darstellung
    import cv2
    l1 = cv2.cvtColor(np.array([[correct]], np.float32) / 255, cv2.COLOR_RGB2LAB)[0, 0]
    l2 = cv2.cvtColor(np.array([[out_px]], np.float32) / 255, cv2.COLOR_RGB2LAB)[0, 0]
    sat = lambda p: (max(p) - min(p)) / max(1, max(p))
    print(f'Patch Quelle(P3) {c}: korrekt in sRGB {correct}  Ergebnis-PNG (untagged=sRGB) {out_px}  '
          f'dE76={np.linalg.norm(l1 - l2):.1f}  Chroma korrekt={np.hypot(*l1[1:]):.1f} Ergebnis={np.hypot(*l2[1:]):.1f}')
