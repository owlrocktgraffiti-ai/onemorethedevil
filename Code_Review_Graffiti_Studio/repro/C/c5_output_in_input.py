"""C5: Ausgabeordner liegt im (oder ist der) Eingabeordner, z.B. Eingabe ~/Downloads und Standardausgabe
~/Downloads/Graffiti_Studio_Ergebnisse. Swift-Filter loadLocal (GraffitiStudio.swift:58-63) schliesst nur
Ergebnisse_*/Vorschau_* und vendor/engine/Referenzkorrekturen/Mockups/Rezepte aus - nicht die eigenen Ausgabenamen
Ordner_*/Foto_*/Instagram/Panorama. Swift-Filter hier 1:1 in Python nachgebildet (Enumerator, skipsHiddenFiles)."""
from common import *
from PIL import Image
import numpy as np, os
work, res = fresh('c5')
sys.path.insert(0, str(res))
from graffiti import list_sources
rng = np.random.default_rng(5)
downloads = work / 'Downloads'; (downloads / 'Urlaub').mkdir(parents=True)
for i in range(3):
    Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((1600, 700)).save(downloads / 'Urlaub' / f'zug{i}.jpg')
output = downloads / 'Graffiti_Studio_Ergebnisse'          # Swift-Standard: ~/Downloads/Graffiti_Studio_Ergebnisse

def swift_load_local(folder):
    ext = {'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp'}; excluded = {'vendor', 'engine', 'Referenzkorrekturen', 'Mockups', 'Rezepte'}
    found = []
    for root, dirs, fs in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith(('Ergebnisse_', 'Vorschau_')) and d not in excluded]
        for f in fs:
            if f.startswith('.') or f.startswith(('Ergebnisse_', 'Vorschau_')) or f in excluded: continue
            if f.rsplit('.', 1)[-1].lower() in ext: found.append(os.path.join(root, f))
    return sorted(found, key=lambda p: os.path.basename(p))

for run in (1, 2):
    photos = swift_load_local(downloads)
    print(f'Lauf {run}: loadLocal(~/Downloads) findet {len(photos)} Fotos; davon aus frueheren Ergebnissen: {sum("Graffiti_Studio_Ergebnisse" in p for p in photos)}')
    out = output / f'Ordner_{run}'
    t = time.monotonic()
    f = final(bridge(res, 'batch', swift_export_library(photos, photos[0], knob(mode='klassisch', scale=1, export='instagram'), {}, out), work))
    print(f'   Export: {f["result"]["images"]} Bilder in {time.monotonic()-t:.1f} s')
photos = swift_load_local(downloads)
print(f'Danach findet loadLocal {len(photos)} Fotos, z.B.:', [str(Path(p).relative_to(downloads)) for p in photos if 'Ordner_2' in p][:6])
py = list_sources(downloads)
print(f'Zum Vergleich graffiti.list_sources (Python-Ausschluesse inkl. Instagram/Panorama): {len(py)} Dateien')
