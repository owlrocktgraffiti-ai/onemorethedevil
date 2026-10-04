"""C12: native_bridge.py:41 validiert ALLE per_photo-Eintraege vor dem Lauf. perPhoto wird beim Ordnerwechsel nie
geleert (GraffitiStudio.swift:49,57-74) und exportLibrary schickt jeden Eintrag mit (:149). Ein einziger ungueltiger Eintrag
(gekreuzte Ecken aus dem Ecken-Editor oder ein geladenes Rezept mit contrast=15) – auch fuer ein Foto eines FRUEHER geoeffneten
Ordners, das gar nicht exportiert wird – verhindert jeden Ordnerexport; die Meldung nennt kein Foto."""
from common import *
from PIL import Image
import numpy as np
work, res = fresh('c12')
rng = np.random.default_rng(12)
src = work / 'Neuer_Ordner'; src.mkdir()
files = []
for i in range(3):
    p = src / f'foto{i}.png'; Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((800, 600)).save(p); files.append(str(p))
old = str(work / 'Alter_Ordner' / 'IMG_0001.jpg')
for tag, bad in [('gekreuzte Ecken (Ecken-Editor)', knob(corners=[[0, 0], [1, 0], [0, 1], [1, 1]], references=False)),
                 ('Rezept mit contrast=15 geladen', knob(values=dict(contrast=15)))]:
    out = work / ('Ordner_' + str(time.time_ns()))
    r = bridge(res, 'batch', swift_export_library(files, files[0], knob(mode='klassisch', scale=1), {old: bad}, out), work)
    print(f'{tag:34s}: Endereignis {final(r)} | Ausgabeordner existiert: {out.exists()}')
