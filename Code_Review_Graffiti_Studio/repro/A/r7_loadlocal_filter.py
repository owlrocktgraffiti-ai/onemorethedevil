"""A8 (teilweise Modell): Ein echter Ordnerexport (Instagram) wird in ein ~/Downloads-aehnliches Verzeichnis
geschrieben (Standard-Ausgabe ~/Downloads/Graffiti_Studio_Ergebnisse). Danach wird die Filterlogik von
StudioModel.loadLocal (GraffitiStudio.swift:58-63, nachgebildet) und Python list_sources (graffiti.py:131-137)
auf ~/Downloads angewendet. Swift steigt zudem in Pakete (.app) ab, da .skipsPackageDescendants fehlt.
"""
from common import *
from PIL import Image
import numpy as np, os
work, res = fresh_resources('r7')
dl = work / 'Downloads'; (dl / 'Urlaub').mkdir(parents=True)
rng = np.random.default_rng(7)
srcs = []
for i in range(2):
    p = dl / 'Urlaub' / f'IMG_000{i}.jpg'; Image.fromarray(rng.integers(0, 255, (300, 900, 3), dtype=np.uint8)).save(p); srcs.append(p)
app_fotos = dl / 'Graffiti Studio.app/Contents/Resources/Fotos'; app_fotos.mkdir(parents=True)
Image.new('RGB', (64, 48)).save(app_fotos / 'IMG_4363.JPG', 'JPEG')
out = dl / 'Graffiti_Studio_Ergebnisse' / 'Ordner_20261004_101010_123'
ev = bridge(res, 'batch', dict(files=[str(p) for p in srcs], output=str(out), settings=dict(export='instagram')), work)['events'][-1]
print('Ordnerexport:', ev['type'], ev.get('result', {}).get('images'), 'Bild(er)')

def swift_loadlocal(folder):
    ext = {'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp'}; excluded = {'vendor', 'engine', 'Referenzkorrekturen', 'Mockups', 'Rezepte'}
    found = []
    for root, dirs, files in os.walk(folder):        # FileManager.enumerator ohne .skipsPackageDescendants
        dirs[:] = [d for d in dirs if not d.startswith('.') and not (d.startswith(('Ergebnisse_', 'Vorschau_')) or d in excluded)]
        for f in files:
            p = Path(root) / f
            if f.startswith('.') or f.startswith(('Ergebnisse_', 'Vorschau_')) or f in excluded: continue
            if p.suffix[1:].lower() in ext and p.is_file() and not p.is_symlink(): found.append(p)
    return sorted(found, key=lambda p: p.name)

sys.path.insert(0, str(res)); from graffiti import list_sources
sw = swift_loadlocal(dl); py = list_sources(dl)
print(f'Swift-Filter (nachgebildet): {len(sw)} "Fotos" geladen, davon {len([p for p in sw if "Graffiti_Studio_Ergebnisse" in str(p)])} aus frueheren Ergebnissen, {len([p for p in sw if ".app" in str(p)])} aus dem App-Paket')
for p in sw: print('   ', p.relative_to(dl))
print(f'Python list_sources: {len(py)} Dateien (schliesst Instagram/Panorama aus, aber nicht Ordner_/Graffiti_Studio_Ergebnisse):')
for p in py: print('   ', p.relative_to(dl))
