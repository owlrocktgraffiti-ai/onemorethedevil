"""A9: Swift schluesselt per_photo mit photo.path (unaufgeloester Pfad aus Enumerator/NSOpenPanel),
studio_backend.batch sucht mit str(source.resolve()) (studio_backend.py:89). Enthaelt der Ordnerpfad einen
Symlink, findet Python die Einzel-Einstellungen nicht -> Ecken/Drehung/Masken/Regler des Fotos werden im
Ordnerexport STILL durch die Basis ersetzt.
"""
from common import *
from PIL import Image
import numpy as np, os
work, res = fresh_resources('r6')
real = work / 'Fotos_echt'; real.mkdir()
Image.fromarray(np.random.default_rng(6).integers(0, 255, (300, 500, 3), dtype=np.uint8)).save(real / 'foto.png')
link = work / 'Fotos_Link'; os.symlink(real, link)
swift_path = str(link / 'foto.png')                    # so liefert FileManager.enumerator(at: link) den Pfad

for key, tag in [(swift_path, 'Schluessel wie Swift (Symlink-Pfad)'), (str(Path(swift_path).resolve()), 'Schluessel aufgeloest')]:
    out = work / ('Ordner_' + str(time.time_ns()))
    ev = bridge(res, 'batch', dict(files=[swift_path], output=str(out), settings={}, per_photo={key: dict(rotation=90)}), work)['events'][-1]
    with Image.open(out / '01_foto.png') as im:
        print(f'{tag:38s} -> Ausgabe {im.size}: {"Drehung 90 angewendet" if im.height > im.width else "Einzel-Drehung IGNORIERT"}')
