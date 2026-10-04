"""C13: Metadaten im Export. render() speichert reines PNG (graffiti.py:125) ohne EXIF; Aufnahmedatum/GPS/Kamera gehen verloren,
die Dateizeit ist die Exportzeit. Gilt auch fuer Instagram-Slides."""
from common import *
from PIL import Image
import numpy as np, os
work, res = fresh('c13')
exif = Image.Exif(); exif[0x0132] = '2019:07:01 18:20:34'; exif[0x010F] = 'Apple'
ifd = exif.get_ifd(0x8769); ifd[0x9003] = '2019:07:01 18:20:34'
p = work / 'IMG_20190701_182034.jpg'
Image.fromarray(np.random.default_rng(13).integers(0, 255, (480, 640, 3), dtype=np.uint8)).save(p, exif=exif)
os.utime(p, (1561998034, 1561998034))
out = work / 'Foto_1'
f = final(bridge(res, 'export', dict(source=str(p), output=str(out / 'IMG_20190701_182034.png'), settings=knob_json(knob(mode='klassisch', scale=1, export='instagram'))), work))
with Image.open(p) as im: print('Quelle EXIF DateTimeOriginal:', im.getexif().get_ifd(0x8769).get(0x9003), '| mtime', time.strftime('%Y-%m-%d', time.localtime(p.stat().st_mtime)))
with Image.open(out / 'IMG_20190701_182034.png') as im: print('Export-PNG EXIF:', dict(im.getexif()) or 'keine', '| info-Schluessel', list(im.info), '| mtime', time.strftime('%Y-%m-%d', time.localtime((out / 'IMG_20190701_182034.png').stat().st_mtime)))
with Image.open(out / 'Instagram' / 'Slide_01.jpg') as im: print('Instagram-Slide EXIF:', dict(im.getexif()) or 'keine')
