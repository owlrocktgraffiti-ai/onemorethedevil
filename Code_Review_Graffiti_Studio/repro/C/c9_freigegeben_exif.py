"""C9: Freigegebenes Bild (Freigegebene_Bilder.json) wird byte-gleich kopiert (graffiti.py:59-63). Danach oeffnen
batch (studio_backend.py:93) und Einzel-Export-Instagram (native_bridge.py:48) die Kopie OHNE exif_transpose.
Bei EXIF-Orientation 6 (typisches Handyfoto) werden Instagram-Slides, Panorama-Eingabe und Vergleichsbild seitlich."""
from common import *
from PIL import Image
import numpy as np
work, res = fresh('c9')
sys.path.insert(0, str(res))
from analysis import digest_image
from graffiti import read_image
src = work / 'Eingabe'; src.mkdir()
# Motiv: Hochformat 800x1200, oben rot, unten blau; gespeichert als 1200x800-Sensorbild mit EXIF Orientation 6.
motif = np.zeros((1200, 800, 3), np.uint8); motif[:600] = (220, 30, 30); motif[600:] = (30, 30, 220)
raw = Image.fromarray(motif).transpose(Image.Transpose.ROTATE_90)       # Sensorlage
exif = Image.Exif(); exif[0x0112] = 6
p = src / 'UZO.JPG'; raw.save(p, quality=95, exif=exif)
shown = read_image(p); print('angezeigtes Original (exif_transpose):', shown.size, 'oben', np.array(shown)[50, 400], 'unten', np.array(shown)[1150, 400])
locked = json.loads((res / 'Freigegebene_Bilder.json').read_text()); locked.append(dict(image_sha256=digest_image(shown), description='Test'))
(res / 'Freigegebene_Bilder.json').write_text(json.dumps(locked))
out = work / 'Ordner_1'
f = final(bridge(res, 'batch', swift_export_library([str(p)], str(p), knob(export='instagram'), {}, out), work))
print('Ordnerexport:', f['type'], tree(out))
s = Image.open(out / 'Instagram/01_UZO/Panorama_Gemeinsame_Basis.png'); a = np.array(s)
print('Instagram-Basis', s.size, '-> Inhalt Breite x Hoehe:', (int((a.max(2) > 20).any(0).sum()), int((a.max(2) > 20).any(1).sum())), '(Motiv ist Hochformat 800x1200)')
cmp_ = np.array(Image.open(out / '01_Vergleich.jpg')); right = cmp_[20:, 390:]
print('Vergleich rechts: Inhalt Breite x Hoehe', (int((right.min(2) < 200).any(0).sum()), int((right.min(2) < 200).any(1).sum())), '; links', (int((cmp_[20:, :390].min(2) < 200).any(0).sum()), int((cmp_[20:, :390].min(2) < 200).any(1).sum())))
r = bridge(res, 'export', dict(source=str(p), output=str(work / 'Foto_1' / 'UZO.png'), settings=knob_json(knob(export='instagram'))), work)
e = final(r); print('Einzelexport:', e['type'], tree(work / 'Foto_1'))
b = np.array(Image.open(work / 'Foto_1/Instagram/Panorama_Gemeinsame_Basis.png'))
print('Einzelexport Instagram: Inhalt Breite x Hoehe', (int((b.max(2) > 20).any(0).sum()), int((b.max(2) > 20).any(1).sum())), '| linke Haelfte Farbe', b[540, 300], 'rechte Haelfte', b[540, 780])
