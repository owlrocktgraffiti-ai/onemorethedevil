"""A6/A7: Im Ecken-Editor (MaskView) koennen sich die Ecken kreuzen bzw. konkav werden - Swift prueft das
nicht. Python lehnt die Einstellungen in native_bridge.py:20 AUSSERHALB des try ab -> kein JSON-Ereignis,
nur Traceback auf stderr. Swift zeigt dann errors.suffix(2000) mit lineLimit(2).
Im Ordnerexport baut native_bridge.py:41 alle per_photo-Settings vorab -> ein einziger ungueltiger Eintrag
(auch fuer ein Foto, das gar nicht exportiert wird) laesst den ganzen Lauf scheitern.
"""
from common import *
from PIL import Image
import numpy as np

work, res = fresh_resources('r2')
rng = np.random.default_rng(2)
srcs = []
for i in range(2):
    p = work / f'foto{i}.jpg'
    Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((800, 600)).save(p); srcs.append(p)

crossed = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]      # Ecke 3 und 4 vertauscht (Fliege)
concave = [[0.0, 0.0], [1.0, 0.0], [0.4, 0.4], [0.0, 1.0]]      # Ecke 3 nach innen gezogen
for name, corners in [('gekreuzt', crossed), ('konkav', concave)]:
    r = bridge(res, 'preview', dict(source=str(srcs[0]), output=str(work / f'{name}.png'), settings=dict(corners=corners)), work)
    print(f'--- Vorschau mit {name}en Ecken: Exitcode', r['returncode'], '| stdout-Ereignisse:', r['events'])
    err = r['stderr'][-2000:]
    print('Swift-Anzeige (erste 2 Zeilen von errors.suffix(2000)):')
    for line in err.splitlines()[:2]: print('   |', line)
    print('Eigentliche Ursache (letzte Zeile):', err.strip().splitlines()[-1])

# Gleiche Ecken im Masken-Vorbereitungslauf (prepare), den MaskView beim Werkzeugwechsel startet
r = bridge(res, 'prepare', dict(source=str(srcs[0]), output=str(work / 'mask.png'), settings=dict(corners=concave)), work)
print('--- prepare mit konkaven Ecken: Exitcode', r['returncode'], '| Ereignisse:', r['events'], '| letzte stderr-Zeile:', r['stderr'].strip().splitlines()[-1])

# Ordnerexport: per_photo enthaelt einen ungueltigen Eintrag fuer ein Foto aus einem FRUEHER geoeffneten Ordner
alt = '/Users/x/Alter_Ordner/IMG_0001.JPG'
req = dict(files=[str(p) for p in srcs], output=str(work / 'Ordner_1'), settings={},
           per_photo={alt: dict(corners=concave)})
r = bridge(res, 'batch', req, work)
print('--- Ordnerexport (2 gueltige Fotos, 1 fremder ungueltiger per_photo-Eintrag):', r['events'][-1], '| Ausgabe existiert:', (work / 'Ordner_1').exists())
