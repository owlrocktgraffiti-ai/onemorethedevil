"""Wird ein eingebettetes ICC-Profil (z. B. Display P3 bei iPhone-JPEGs) bis in die Vorschau/Export-PNG getragen?"""
import sys, pathlib
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
from PIL import Image, ImageCms
import graffiti
from studio_backend import render_one
from adjustments import Settings
work = HERE / 'out_t12'; work.mkdir(exist_ok=True)
prof = ImageCms.ImageCmsProfile(ImageCms.createProfile('LAB')).tobytes()  # beliebiges Nicht-sRGB-Profil als Platzhalter
p = work / 'icc_quelle.jpg'; Image.new('RGB', (600, 400), (200, 50, 50)).save(p, icc_profile=prof)
graffiti.SESSION.update(ai_available=False, ocr_available=False)
for label, s in [('ohne Ecken', Settings(mode='klassisch')), ('mit Ecken (transform)', Settings(mode='klassisch', corners=[[0,0],[1,0],[1,1],[0,1]]))]:
    r = render_one(p, work / f'icc_{label[:4]}.png', s, False)
    print(label, '-> Quelle ICC', len(Image.open(p).info.get('icc_profile', b'')), 'Byte; Ausgabe-PNG ICC', len(Image.open(r['image']).info.get('icc_profile', b'') or b''), 'Byte')
