# D13: EXIF in Ergebnissen
from common import *
import numpy as np
from PIL import Image
import graffiti
from adjustments import Settings
from studio_backend import render_one
ex=Image.Exif();ex[0x0110]='iPhone 13';ex[0x0132]='2024:05:01 12:00:00'
ex.get_ifd(0x8769)[0x9003]='2024:05:01 12:00:00';ex.get_ifd(0x8825).update({1:'N',2:(52.0,31.0,12.0)})
Image.fromarray(np.random.default_rng(1).integers(0,255,(300,400,3),dtype=np.uint8)).save(OUT/'exif_src.jpg',exif=ex.tobytes())
im=graffiti.read_image(OUT/'exif_src.jpg');print('read_image info exif:',len(im.info.get('exif') or b''),'B')
for prof in ('originalnah','kraeftig'):
    r=render_one(OUT/'exif_src.jpg',OUT/f'exif_{prof}.png',Settings(profile=prof,mode='klassisch'))
    with Image.open(r['image']) as o:e=o.getexif();print(prof,'Ergebnis EXIF-Tags',len(e),'DateTimeOriginal',e.get_ifd(0x8769).get(0x9003))
# direkter Test: Bild mit info['exif'] als PNG speichern
im.save(OUT/'exif_direct.png');print('PNG direkt aus read_image: EXIF-Tags',len(Image.open(OUT/'exif_direct.png').getexif()))
