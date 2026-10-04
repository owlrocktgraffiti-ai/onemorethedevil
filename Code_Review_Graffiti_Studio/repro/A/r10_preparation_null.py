"""A10: receive() markiert ein Foto als "Abzüge", wenn plan["preparation"] != nil (GraffitiStudio.swift:132).
Python liefert fuer JEDES Foto ohne Abzug "preparation": null (analysis.py:96). JSONSerialization macht daraus
NSNull, und NSNull != nil ist in Swift wahr -> jedes vorgeschaute Foto landet im Filter "Abzüge" und verliert
"Wände"/"Züge".
"""
from common import *
from PIL import Image
import numpy as np
work, res = fresh_resources('r10')
src = work / 'IMG_20190701_999999.jpg'           # Swift-Typ "Wände" (Praefix IMG_20190701)
Image.fromarray(np.random.default_rng(10).integers(0, 255, (600, 800, 3), dtype=np.uint8)).save(src, quality=90)
r = bridge(res, 'preview', dict(source=str(src), output=str(work / 'p.png'), settings=dict(mode='klassisch')), work)
line = [l for l in json.dumps(r['events'][-1], ensure_ascii=False).split(', ') if '"preparation"' in l]
print('Ergebnisereignis enthaelt:', line)
print('Schluessel vorhanden:', 'preparation' in r['events'][-1]['result']['analysis'], '| Wert:', r['events'][-1]['result']['analysis']['preparation'])
