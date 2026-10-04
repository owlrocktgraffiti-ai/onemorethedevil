"""D1b: ICC im Ergebnis abhängig vom gewählten Startprofil/Regler (gleiches P3-Foto aus t1)."""
from PIL import Image
import common
from adjustments import Settings
from studio_backend import render_one
src=common.OUT/'t1'/'p3_exif.jpg'
for prof in ('originalnah','kraeftig','nacht'):
    for preview in (True,False):
        r=render_one(src,common.OUT/'t1'/f'prof_{prof}_{preview}.png',Settings(mode='klassisch',profile=prof),preview=preview)
        im=Image.open(r['image']);print(f'Profil {prof:11s} {"Vorschau" if preview else "Export  "}: icc_profile im PNG = {"ja" if im.info.get("icc_profile") else "NEIN"}; Rot-Patch = {im.convert("RGB").getpixel((im.width//6,im.height//4))}')
