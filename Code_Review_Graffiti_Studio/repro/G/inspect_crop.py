"""Misst, ob eine Vorschau den Tisch (braun) und den Nachbarabzug (blau) noch enthaelt und ob das Rezept lief.
Farbtonbasiert (die Regler veraendern Helligkeit/Saettigung, kaum den Farbton).
Aufruf (CWD=runX): python inspect_crop.py  -> nutzt work/native_tests/crop.png und crop.json aus dem Bridge-Test"""
import json, numpy as np
from PIL import Image
im = Image.open('work/native_tests/crop.png').convert('RGB')
h, s, v = [np.asarray(c).astype(float) for c in im.convert('HSV').split()]
hue = h / 255 * 360
table = (hue > 12) & (hue < 38) & (s > 80) & (v < 200)
blue = (hue > 200) & (hue < 245) & (s > 80)
plan = json.load(open('work/native_tests/crop.json'))
print('Ausgabegroesse', im.size, '| Anteil Tisch(braun) %.3f | Anteil Nachbarabzug(blau) %.3f' % (table.mean(), blue.mean()))
print('executed:', plan.get('executed'))
print('warnings:', plan.get('warnings'))
