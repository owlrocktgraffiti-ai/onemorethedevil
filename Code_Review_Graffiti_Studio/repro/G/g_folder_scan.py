"""Testluecke: test_native_bridge.py:25-28 prueft graffiti.list_sources und den Bruecken-Befehl 'list'.
Die App nutzt beides NICHT (Swift ruft nur preview/prepare/export/batch, Swift:90,144,146,150), sondern loadLocal (Swift:57-74).
Hier: Nachbildung von loadLocal vs. list_sources auf einem Downloads-aehnlichen Ordner, in dem der
Standard-Ausgabeordner (Swift:47 ~/Downloads/Graffiti_Studio_Ergebnisse) schon Ergebnisse enthaelt."""
import sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
from pathlib import Path
from PIL import Image
res = fresh_resources('scan'); dl = res.parent / 'Downloads'
files = ['Fotos/zug1.jpg', 'Fotos/Unterordner/wand.PNG', 'Fotos/.versteckt/alt.jpg', 'Fotos/._zug1.jpg',
         'Graffiti_Studio_Ergebnisse/Ordner_20261004_101010_000/01_zug1.png', 'Graffiti_Studio_Ergebnisse/Ordner_20261004_101010_000/01_Vergleich.jpg',
         'Graffiti_Studio_Ergebnisse/Ordner_20261004_101010_000/Instagram/01_zug1/Slide_01.jpg',
         'Graffiti_Studio_Ergebnisse/Ordner_20261004_101010_000/Instagram/01_zug1/Panorama_Gemeinsame_Basis.png',
         'Graffiti_Studio_Ergebnisse/Foto_20261004_101500_000/zug1.png']
for f in files:
    p = dl / f; p.parent.mkdir(parents=True, exist_ok=True); Image.new('RGB', (64, 48), (10, 20, 30)).save(p, format='PNG' if f.lower().endswith('png') else 'JPEG')
def swift_loadLocal(folder):  # Swift:58-66 nachgebildet (.skipsHiddenFiles, excluded, Prefixe)
    ext = {'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp'}; excluded = {'vendor', 'engine', 'Referenzkorrekturen', 'Mockups', 'Rezepte'}; found = []
    for root, dirs, fs in os.walk(folder):
        dirs[:] = sorted(d for d in dirs if not d.startswith('.') and not d.startswith(('Ergebnisse_', 'Vorschau_')) and d not in excluded)
        for f in sorted(fs):
            if f.startswith('.') or f.startswith(('Ergebnisse_', 'Vorschau_')) or f in excluded: continue
            if f.rsplit('.', 1)[-1].lower() in ext: found.append(os.path.relpath(os.path.join(root, f), folder))
    return sorted(found)
code, out, err = py_in(res, f'from graffiti import list_sources;from pathlib import Path;p=Path({str(dl)!r});print("\\n".join(str(x.relative_to(p)) for x in list_sources(p)))')
print('Swift loadLocal (nachgebildet):'); [print('   ', x) for x in swift_loadLocal(dl)]
print('Python list_sources (vom Test geprueft):'); [print('   ', x) for x in out.split()]
