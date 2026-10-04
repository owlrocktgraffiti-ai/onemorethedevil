"""graffiti.read_image: Image.open -> exif_transpose -> convert('RGB') bei 16-Bit-Graustufen (PNG/TIFF), 16-Bit-RGB,
CMYK-JPEG und eingebettetem ICC-Profil. Gemessen: mittlere Helligkeit gegenueber dem erwarteten 8-Bit-Wert."""
import sys, io, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
import numpy as np
from PIL import Image, ImageCms
from graffiti import read_image
work = HERE / 'out_t12'; work.mkdir(exist_ok=True)

# 16-Bit-Graustufen: Verlauf 0..65535 (wie ein 16-Bit-Scan eines Abzugs)
g = np.tile(np.linspace(0, 65535, 512).astype(np.uint16), (128, 1))
for ext in ('png', 'tif'):
    p = work / f'grau16.{ext}'; Image.fromarray(g).save(p)
    src = Image.open(p); im = read_image(p); a = np.array(im)
    exp = (g / 257).round()
    print(f'16-Bit-Grau .{ext}: Pillow-Modus {src.mode:6s} -> read_image Mittel {a.mean():6.1f} (erwartet {exp.mean():.1f}), Anteil reinweiss {(a.min(axis=2) == 255).mean():.2f} (erwartet {(exp == 255).mean():.2f})')

# 16-Bit-RGB-PNG ueber OpenCV schreiben (Pillow kann 48-Bit nicht schreiben)
import cv2
rgb16 = np.zeros((64, 256, 3), np.uint16); rgb16[:, :, 0] = np.linspace(0, 65535, 256).astype(np.uint16)
cv2.imwrite(str(work / 'rgb16.png'), rgb16[:, :, ::-1])
im = read_image(work / 'rgb16.png'); print(f'16-Bit-RGB .png: Pillow-Modus {Image.open(work / "rgb16.png").mode} -> R-Mittel {np.array(im)[:, :, 0].mean():.1f} (erwartet {(rgb16[:, :, 0] / 257).mean():.1f})')

# ICC-Profil: wird es in die Weiterverarbeitung/Ausgabe getragen?
srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
p = work / 'mit_icc.jpg'; Image.new('RGB', (64, 64), (200, 50, 50)).save(p, icc_profile=srgb)
im = read_image(p)
print('JPEG mit ICC: Quelle icc_profile', len(Image.open(p).info.get('icc_profile', b'')), 'Byte -> nach read_image', len(im.info.get('icc_profile', b'') or b''), 'Byte')
