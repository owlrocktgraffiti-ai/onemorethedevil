"""Ordnerexport: per_photo-Schluessel (Swift: photo.path, unaufgeloest) vs. Python-Lookup str(source.resolve()).
Ordner wird ueber einen symbolischen Link geoeffnet (wie /tmp -> /private/tmp auf macOS oder ein verlinkter Fotoordner).
Erwartung: Ecken/Masken des Fotos werden im Ordnerexport angewendet."""
import sys, os, json, pathlib, shutil, subprocess
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / 'Resources'
from PIL import Image
work = HERE / 'out_t11'
shutil.rmtree(work, ignore_errors=True); (work / 'echt').mkdir(parents=True)
Image.new('RGB', (1000, 800), (120, 120, 120)).save(work / 'echt' / 'foto.png')
os.symlink(work / 'echt', work / 'link')
photo = str(work / 'link' / 'foto.png')  # so liefert der FileManager-Enumerator den Pfad, wenn der Ordner ueber den Link geoeffnet wurde
base = dict(values={}, profile='auto', mode='klassisch', scale=1, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])
mine = dict(base, corners=[[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]], rotation=0)  # Nutzer hat Ausschnitt gesetzt
req = work / 'req.json'
req.write_text(json.dumps(dict(files=[photo], output=str(work / 'Ordner_1'), settings=base, per_photo={photo: mine})))
r = subprocess.run([sys.executable, str(RES / 'native_bridge.py'), 'batch', '--request', str(req)], capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
res = [json.loads(l) for l in r.stdout.splitlines() if '"result"' in l]
print('Exitcode', r.returncode, '| Ergebnis-Ereignis:', bool(res))
out = sorted((work / 'Ordner_1').glob('01_*.png'))[0]
print('erwartete Groesse mit Nutzer-Ausschnitt: 500x400 | tatsaechlich:', Image.open(out).size)
print('per_photo-Schluessel:', photo, '\nPython sucht nach   :', str(pathlib.Path(photo).resolve()))
