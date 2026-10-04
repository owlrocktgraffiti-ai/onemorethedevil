"""Hinweis 7: EXIF-/Orientierungsquellen, die Pillow (graffiti.read_image -> ImageOps.exif_transpose) auswertet.
Nur die Pillow-Seite ist hier ausfuehrbar; die Swift-Seite (CGImageSourceCreateThumbnailAtIndex mit
kCGImageSourceCreateThumbnailWithTransform) laesst sich ohne macOS nicht pruefen."""
import sys, io, pathlib, zlib, struct
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'Resources'))
from PIL import Image, PngImagePlugin
from graffiti import read_image
work = HERE / 'out_t7'; work.mkdir(exist_ok=True)
base = Image.new('RGB', (300, 200), (128, 128, 128)); base.paste((255, 0, 0), (0, 0, 60, 40))

def exif_bytes(orientation):
    e = Image.Exif(); e[0x0112] = orientation; return e.tobytes()

def check(name, path):
    try:
        im = read_image(path); w, h = im.size
        corners = {'oben links': (5, 5), 'oben rechts': (w - 6, 5), 'unten links': (5, h - 6), 'unten rechts': (w - 6, h - 6)}
        red = [k for k, xy in corners.items() if (lambda p: p[0] > 200 and p[1] < 60)(im.getpixel(xy))]
        print(f'{name:58s} -> read_image {w}x{h}, rote Ecke: {red}')
    except Exception as e:
        print(f'{name:58s} -> FEHLER {type(e).__name__}: {e}')

for o in (1, 6, 8, 3, 0, 9, 255):
    p = work / f'jpg_o{o}.jpg'; base.save(p, exif=exif_bytes(o)); check(f'JPEG EXIF Orientation={o}', p)
p = work / 'png_exif6.png'; base.save(p, exif=exif_bytes(6)); check('PNG eXIf-Chunk Orientation=6', p)
# ImageMagick-Stil: EXIF als Hex im tEXt "Raw profile type exif"
raw = b'Exif\x00\x00' + exif_bytes(6)
hexed = '\nexif\n' + f'{len(raw):8d}' + '\n' + raw.hex() + '\n'
info = PngImagePlugin.PngInfo(); info.add_text('Raw profile type exif', hexed)
p = work / 'png_rawprofile6.png'; base.save(p, pnginfo=info); check('PNG tEXt "Raw profile type exif" Orientation=6', p)
# XMP-Orientierung ohne EXIF
xmp = '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description xmlns:tiff="http://ns.adobe.com/tiff/1.0/" tiff:Orientation="6"/></rdf:RDF></x:xmpmeta>'
info = PngImagePlugin.PngInfo(); info.add_itxt('XML:com.adobe.xmp', xmp)
p = work / 'png_xmp6.png'; base.save(p, pnginfo=info); check('PNG iTXt XMP tiff:Orientation=6 (ohne EXIF)', p)
p = work / 'jpg_xmp6.jpg'; base.save(p, xmp=xmp.encode()); check('JPEG nur XMP tiff:Orientation=6 (ohne EXIF)', p)
p = work / 'webp_exif6.webp'; base.save(p, exif=exif_bytes(6), lossless=True); check('WebP EXIF Orientation=6', p)
p = work / 'tif_o6.tif'; base.save(p, tiffinfo={274: 6}); check('TIFF Tag 274 Orientation=6', p)
# Defekte EXIF-Daten
good = bytearray(base.tobytes())
p = work / 'jpg_kaputt.jpg'; buf = io.BytesIO(); base.save(buf, 'JPEG', exif=b'Exif\x00\x00MM\x00\x2a\x00\x00\x00\x08\x00\x05\x01\x12'); p.write_bytes(buf.getvalue()); check('JPEG mit abgeschnittenem EXIF-IFD', p)
