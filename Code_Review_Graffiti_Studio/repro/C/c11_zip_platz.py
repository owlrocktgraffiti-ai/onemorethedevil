"""C11: Fehler NACH dem Schreiben der Bilder (hier: Ziel-Datentraeger voll beim ZIP, studio_backend.py:117-121) ->
gesamter Ordnerexport meldet 'error', obwohl alle Bilder, CSV und Bericht geschrieben wurden; halbe ZIP bleibt liegen.
Ausgabe auf ein 20-MB-tmpfs (Ersatz fuer volle Platte/USB-Stick). Bilder = Rauschen (PNG kaum komprimierbar)."""
from common import *
from PIL import Image
import numpy as np, zipfile
work, res = fresh('c11')
mnt = HERE / 'work' / 'tmpfs_test'   # vorher: mount -t tmpfs -o size=20m tmpfs <mnt>
for p in mnt.iterdir():
    shutil.rmtree(p) if p.is_dir() else p.unlink()
rng = np.random.default_rng(11)
src = work / 'Eingabe'; src.mkdir()
files = []
for i in range(5):
    p = src / f'foto{i}.png'; Image.fromarray(rng.integers(0, 255, (800, 1000, 3), dtype=np.uint8)).save(p); files.append(str(p))
out = mnt / 'Graffiti_Studio_Ergebnisse' / 'Ordner_1'
r = bridge(res, 'batch', swift_export_library(files, files[0], knob(mode='klassisch', scale=1, values=dict(sharpness=0, clarity=0, denoise=0)), {}, out), work)
f = final(r)
print('Endereignis:', f)
print('Ordnerinhalt:', tree(out))
z = out.with_suffix('.zip'); print('ZIP-Datei vorhanden:', z.exists(), z.stat().st_size if z.exists() else '')
if z.exists():
    try:
        with zipfile.ZipFile(z) as zz: print('ZIP lesbar:', zz.testzip())
    except Exception as e: print('ZIP defekt:', type(e).__name__, e)
