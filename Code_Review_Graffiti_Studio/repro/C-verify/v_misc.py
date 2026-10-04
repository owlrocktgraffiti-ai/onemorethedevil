"""Gegenpruefung C6 (stitch-Aufwand/Abbruch), C7 (Karussell), C8 (Swift-Filter loadLocal), C12 (EXIF bei Freigabe)."""
import sys, json, os, shutil, time, threading, inspect
from pathlib import Path
HERE = Path(__file__).resolve().parent
RES = HERE / 'Resources'; sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image
W = HERE / 'work_misc'; shutil.rmtree(W, ignore_errors=True); W.mkdir()
import exports

print('--- C6 ---')
print('stitch-Signatur:', inspect.signature(exports.stitch))
calls = {'overlap': 0, 'sift': 0}
orig_overlap = exports.overlap
import cv2
orig_sift = cv2.SIFT_create
def counting_sift(*a, **k):
    calls['sift'] += 1; return orig_sift(*a, **k)
exports.cv2.SIFT_create = counting_sift
def counting_overlap(a, b):
    calls['overlap'] += 1; return orig_overlap(a, b)
exports.overlap = counting_overlap
rng = np.random.default_rng(5)
for n in (4, 8):
    calls.update(overlap=0, sift=0)
    imgs = [Image.fromarray(rng.integers(0, 255, (60, 80, 3)).astype(np.uint8)).resize((1200, 900)) for _ in range(n)]
    t = time.time()
    try: exports.stitch(imgs, W / f'pano{n}')
    except ValueError as e: msg = str(e)[:50]
    print(f'n={n}: overlap-Aufrufe={calls["overlap"]} SIFT-Instanzen={calls["sift"]} Dauer={time.time()-t:.1f}s -> {msg}')
exports.overlap = orig_overlap; exports.cv2.SIFT_create = orig_sift

print('--- C7 ---')
for ratio in (1.5, 1.9, 2.1, 2.7, 4.0, 0.8):
    h = 1000; w = int(round(ratio * h))
    img = Image.new('RGB', (w, h), (128, 128, 128)); f = W / f'car_{ratio}'
    n = exports.carousel(img, f)
    blk = []
    for i in range(n):
        a = np.array(Image.open(f / f'Slide_{i+1:02d}.jpg')); blk.append(round(100 * float((a.max(axis=2) < 30).mean()), 1))
    print(f'ratio {ratio}: {n} Slides {Image.open(f / "Slide_01.jpg").size}, Schwarzanteil % {blk}')

print('--- C8 Nachbildung Swift loadLocal (Zeile 58-63) ---')
dl = W / 'Downloads'; (dl).mkdir()
for nm in ('a.jpg', 'b.jpg'): Image.new('RGB', (50, 50)).save(dl / nm)
outdir = dl / 'Graffiti_Studio_Ergebnisse' / 'Ordner_20261004_120000_000'; (outdir / 'Instagram' / '01_a').mkdir(parents=True)
for nm in ('01_a.png', '01_Vergleich.jpg', 'Instagram/01_a/Slide_01.jpg', 'Instagram/01_a/Panorama_Gemeinsame_Basis.png'):
    Image.new('RGB', (50, 50)).save(outdir / nm)
ext = {'jpg', 'jpeg', 'png', 'tif', 'tiff', 'webp'}; excluded = {'vendor', 'engine', 'Referenzkorrekturen', 'Mockups', 'Rezepte'}
found = []
for root, dirs, files in os.walk(dl):
    dirs[:] = [d for d in dirs if not d.startswith('.') and not (d.startswith('Ergebnisse_') or d.startswith('Vorschau_') or d in excluded)]
    for fn in files:
        if fn.startswith('.') or fn.startswith('Ergebnisse_') or fn.startswith('Vorschau_') or fn in excluded: continue
        if fn.rsplit('.', 1)[-1].lower() in ext: found.append(str((Path(root) / fn).relative_to(dl)))
print('loadLocal(~/Downloads) findet:', sorted(found))

print('--- C12 freigegebenes Bild mit EXIF-Orientation 6 ---')
from graffiti import read_image
from analysis import digest_image
a = np.zeros((800, 1200, 3), np.uint8); a[:, :600] = (30, 30, 220); a[:, 600:] = (220, 30, 30)  # gespeichert: links blau, rechts rot
src = W / 'frei' / 'UZO.JPG'; src.parent.mkdir()
ex = Image.Exif(); ex[0x0112] = 6; Image.fromarray(a).save(src, exif=ex, quality=95)
shown = read_image(src); print('angezeigt (exif_transpose):', shown.size, 'oben', np.array(shown)[50, 400], 'unten', np.array(shown)[1150, 400])
lf = RES / 'Freigegebene_Bilder.json'; orig = lf.read_text()
lf.write_text(json.dumps(json.loads(orig) + [dict(image_sha256=digest_image(shown))]))
try:
    from adjustments import Settings
    from studio_backend import batch_files
    r = batch_files([src], W / 'out_c12', Settings(mode='klassisch', scale=1, export='instagram'))
    out = W / 'out_c12'; print('Dateien:', sorted(p.name for p in out.iterdir()))
    base = Image.open(next(out.rglob('Panorama_Gemeinsame_Basis.png'))); b = np.array(base)
    nz = np.argwhere(b.max(axis=2) > 20); (y0, x0), (y1, x1) = nz.min(0), nz.max(0)
    print('Instagram-Basis', base.size, 'Inhalt B x H:', (x1 - x0 + 1, y1 - y0 + 1), 'links', b[540, x0 + 5], 'rechts', b[540, x1 - 5])
finally:
    lf.write_text(orig)
