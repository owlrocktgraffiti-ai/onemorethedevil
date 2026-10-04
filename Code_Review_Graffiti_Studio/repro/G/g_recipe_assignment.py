"""Regressionstest-Vorschlag Rezeptzuordnung (nicht in den ausgelieferten Tests):
 (1) umbenannte Kopie des bekannten Abzugs -> Rezept per Fingerabdruck
 (2) gleicher Name + gleiche Groesse, anderer Inhalt -> KEIN Rezept
 (3) gleicher Inhalt, nur neu JPEG-komprimiert -> Fingerabdruck weicht ab -> kein Rezept (Doku: 'Neue JPEG-Kompression verlangt neue Pruefung')"""
import sys, json, shutil, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
from PIL import Image
res = fresh_resources('recipe'); wd = res.parent
subprocess.run([PY, str(G / 'make_synth.py'), str(res), 'exif6'], check=True, capture_output=True)
subprocess.run([PY, str(G / 'make_synth.py'), str(res), 'inject'], check=True, capture_output=True)
src = res / 'Fotos' / 'IMG_4363.JPG'
(wd / 'umbenannt').mkdir(); shutil.copy2(src, wd / 'umbenannt' / 'Abzug_vom_Tisch.jpg')
(wd / 'anders').mkdir(); im = Image.open(src); im2 = im.copy(); im2.putpixel((5, 5), (0, 0, 0)); im2.save(wd / 'anders' / 'IMG_4363.JPG', quality=92, exif=im.info.get('exif'))
(wd / 'rekomp').mkdir(); im.save(wd / 'rekomp' / 'IMG_4363.JPG', quality=80, exif=im.info.get('exif'))
for label, p in [('(1) umbenannt', wd / 'umbenannt/Abzug_vom_Tisch.jpg'), ('(2) gleicher Name, anderer Inhalt', wd / 'anders/IMG_4363.JPG'), ('(3) neu komprimiert', wd / 'rekomp/IMG_4363.JPG')]:
    code, ev, err = bridge(res, 'preview', dict(source=str(p), output=str(wd / (label[:3].strip('()') + '.png')), settings=dict(mode='klassisch', scale=1)), wd)
    plan = ev[-1]['result']['analysis']
    print(f'{label:36} Rezept ausgefuehrt: {"Fotorezept ausgeführt." in plan["executed"]!s:5} Ausgabe {Image.open(ev[-1]["result"]["image"]).size} Warnungen: {plan["warnings"][:2]}')
