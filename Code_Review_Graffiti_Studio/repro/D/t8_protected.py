"""D9: Freigegebene (geschützte) Bilder – Regler ohne Wirkung/ohne Hinweis; EXIF-Drehung im Stapel-Vergleich/Instagram."""
import json, shutil, hashlib
import numpy as np
from PIL import Image
import common
from graffiti import read_image
from analysis import digest_image
from adjustments import Settings
from studio_backend import render_one, batch_files

OUT = common.OUT / 't8'
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
# Querformatig gespeichert, EXIF-Orientierung 6 => wird hochkant angezeigt (typisch iPhone)
a = np.zeros((300, 400, 3), np.uint8); a[:, :200] = (200, 30, 30); a[:, 200:] = (30, 30, 200)
exif = Image.Exif(); exif[0x0112] = 6
src = OUT / 'freigabe.jpg'; Image.fromarray(a).save(src, quality=95, exif=exif)
digest = digest_image(read_image(src))
locked = common.RES / 'Freigegebene_Bilder.json'
backup = locked.read_text()
locked.write_text(json.dumps(json.loads(backup) + [dict(image_sha256=digest, description='Test')]))
try:
    sha_src = hashlib.sha256(src.read_bytes()).hexdigest()
    for vals in ({}, {'exposure': 100, 'saturation': -100}, {'exposure': -100}):
        r = render_one(src, OUT / 'vorschau.png', Settings(values=vals, scale=4), preview=True)
        an = r['analysis']
        print(f'Vorschau {vals}: Datei={r["image"].split("/")[-1]} byte-identisch zum Original={hashlib.sha256(open(r["image"],"rb").read()).hexdigest()==sha_src} '
              f'Größe={Image.open(r["image"]).size} controls.exposure={an["controls"]["exposure"]} Warnungen={an["warnings"]} backend={an["effective_backend"]}')
    res = batch_files([src], OUT / 'Stapel', Settings(export='instagram', values={'exposure': 50}))
    print('Stapel:', {k: res[k] for k in ('images', 'total', 'warnings')})
    cmp_ = np.array(Image.open(OUT / 'Stapel' / '01_Vergleich.jpg')).astype(int)
    left = cmp_[20:270, 0:380]; right = cmp_[20:270, 390:770]
    def bbox(x):
        m = (np.abs(x - 238).sum(axis=2) > 60); ys, xs = np.where(m); return (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    print('Vergleich: Original-Kachel (B,H)=', bbox(left), ' Ergebnis-Kachel (B,H)=', bbox(right))
    slide = Image.open(OUT / 'Stapel' / 'Instagram' / '01_freigabe' / 'Slide_01.jpg'); s = np.array(slide).astype(int)
    m = s.sum(axis=2) > 60; ys, xs = np.where(m)
    print('Instagram-Slide Inhalt (B,H)=', (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1), '; angezeigtes Original (B,H)=', read_image(src).size)
finally:
    locked.write_text(backup)
