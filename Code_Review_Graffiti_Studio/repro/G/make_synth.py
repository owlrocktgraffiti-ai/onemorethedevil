"""Synthetischer Ersatz fuer IMG_4363.JPG (Abzug seitlich auf Tisch, mit Nachbarabzug).

Aufruf:
  python make_synth.py <Resources-Kopie> exif6        -> 4032x3024 gespeichert + EXIF Orientation 6 (Anzeige 3024x4032)
  python make_synth.py <Resources-Kopie> landscape    -> 4032x3024 ohne EXIF (z. B. re-exportierte Kopie)
  python make_synth.py <Resources-Kopie> inject       -> Pixel-Fingerabdruck der vorhandenen Fotos/IMG_4363.JPG
                                                         in die KOPIE von Fotorezepte.json eintragen
Nur Kopien werden veraendert.
"""
import sys, json
from pathlib import Path
from PIL import Image, ImageDraw

TABLE = (120, 72, 38)      # braun
PAPER = (236, 232, 222)    # hell
NEIGH = (60, 90, 170)      # Nachbarabzug (blau)


def portrait():
    W, H = 3024, 4032
    im = Image.new('RGB', (W, H), TABLE)
    d = ImageDraw.Draw(im)
    # Abzug an den Rezeptecken von IMG_4363 (normiert, Anzeige-Orientierung)
    corners = [[0.012, 0.034], [0.847, 0.039], [0.856, 0.927], [0.087, 0.943]]
    d.polygon([(x * (W - 1), y * (H - 1)) for x, y in corners], fill=PAPER)
    # Nachbarabzug rechts ausserhalb des Rezeptausschnitts
    d.rectangle([int(0.88 * W), int(0.10 * H), W - 1, int(0.80 * H)], fill=NEIGH)
    # "Graffiti" seitlich: Balken quer, damit nach 90-Grad-Drehung waagerecht
    for i, c in enumerate([(220, 30, 30), (30, 160, 60), (240, 200, 20), (20, 20, 20)]):
        x0 = int(W * (0.15 + 0.15 * i)); d.rectangle([x0, int(H * 0.2), x0 + 250, int(H * 0.8)], fill=c)
    return im


def main():
    res = Path(sys.argv[1]); variant = sys.argv[2]
    path = res / 'Fotos' / 'IMG_4363.JPG'; path.parent.mkdir(parents=True, exist_ok=True)
    if variant == 'exif6':
        raw = portrait().transpose(Image.Transpose.ROTATE_90)  # gespeichert quer
        exif = Image.Exif(); exif[0x0112] = 6
        raw.save(path, quality=92, exif=exif.tobytes())
    elif variant == 'landscape':
        raw = portrait().transpose(Image.Transpose.ROTATE_90)
        raw.save(path, quality=92)
    elif variant == 'inject':
        sys.path.insert(0, str(res))
        from graffiti import read_image
        from analysis import digest_image
        fp = digest_image(read_image(path))
        rec = json.loads((res / 'Fotorezepte.json').read_text())
        rec['IMG_4363.JPG']['image_sha256'] = fp
        (res / 'Fotorezepte.json').write_text(json.dumps(rec, indent=2))
        print('injected', fp)
        return
    with Image.open(path) as im:
        print(variant, 'gespeichert', im.size, 'EXIF-Orientation', im.getexif().get(0x0112))


if __name__ == '__main__':
    main()
