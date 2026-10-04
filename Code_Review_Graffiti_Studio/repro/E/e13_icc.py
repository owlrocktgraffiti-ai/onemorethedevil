"""Eingebettetes Farbprofil (z. B. Display P3 bei iPhone-JPEGs) wird beim Lesen ignoriert und fehlt in der Ausgabe-PNG."""
from common import *
from PIL import ImageCms
import graffiti
from studio_backend import render_one
from adjustments import Settings
prof=ImageCms.ImageCmsProfile(ImageCms.createProfile('LAB')).tobytes()  # Platzhalter für ein Nicht-sRGB-Profil (P3 nicht offline verfügbar)
im=Image.fromarray(np.random.default_rng(3).integers(0,255,(300,400,3),dtype=np.uint8))
src=OUT/'e13_mit_profil.jpg';im.save(src,quality=92,icc_profile=prof)
with Image.open(src) as s:print('Quelle: icc_profile vorhanden:',bool(s.info.get('icc_profile')),len(s.info.get('icc_profile',b'')),'Bytes')
print('read_image().info enthält icc_profile:',bool(graffiti.read_image(src).info.get('icc_profile')))
for preview in (True,False):
    r=render_one(src,OUT/f'e13_{"vorschau" if preview else "export"}.png',Settings(mode='klassisch'),preview)
    with Image.open(r['image']) as o:print('Vorschau' if preview else 'Export','-> PNG icc_profile vorhanden:',bool(o.info.get('icc_profile')),'| info-Schlüssel:',list(o.info))
