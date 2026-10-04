"""Eigene Gegenpruefung B8/B9/B10/B12/B15. Nur Kopie ./Resources, Ausgaben in ./out_v2."""
import sys, json, subprocess, hashlib, os, shutil, io
from pathlib import Path
HERE = Path(__file__).resolve().parent; RES = HERE / 'Resources'
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image, ImageCms
OUT = HERE / 'out_v2'
shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()

def bridge(cmd, req):
    p = OUT / f'req_{cmd}.json'; p.write_text(json.dumps(req))
    r = subprocess.run([sys.executable, str(RES / 'native_bridge.py'), cmd, '--request', str(p)], capture_output=True, text=True)
    ev = [json.loads(l) for l in r.stdout.splitlines() if l.strip().startswith('{')]
    return r, ev

src = OUT / 'foto.png'
Image.fromarray(np.random.default_rng(2).integers(0, 255, (3000, 4000, 3), dtype=np.uint8)).save(src)

# B9/B8: gekreuzte Ecken
crossed = [[1, 0], [0, 0], [1, 1], [0, 1]]
for cmd in ('preview', 'prepare'):
    r, ev = bridge(cmd, dict(source=str(src), output=str(OUT / f'{cmd}.png'), settings=dict(corners=crossed)))
    tail = r.stderr.strip().splitlines()
    swift = r.stderr[-2000:].split('\n')[:2]   # errors.suffix(2000) + lineLimit(2)
    print(f'B9 {cmd} gekreuzt: Exit {r.returncode} | Ereignisse {[e["type"] for e in ev]} | Swift-Zeilen {swift} | letzte Zeile {tail[-1]!r}')
# B8: schmaler Streifen 2,5 % Breite
narrow = [[.40, 0], [.425, 0], [.425, 1], [.40, 1]]
r, ev = bridge('prepare', dict(source=str(src), output=str(OUT / 'narrow.png'), settings=dict(corners=narrow)))
print('B8 schmal prepare: Exit', r.returncode, 'Ereignisse', [(e['type'], e.get('message')) for e in ev])
from photo_prepare import transform
from graffiti import read_image
print('B8 gleicher Ausschnitt in Vollaufloesung:', transform(read_image(src), dict(corners=narrow)).size)

# B10: Symlink im Ordnerpfad
real = OUT / 'echt'; real.mkdir(); link = OUT / 'link'; link.symlink_to(real, target_is_directory=True)
Image.fromarray(np.random.default_rng(3).integers(0, 255, (800, 1000, 3), dtype=np.uint8)).save(real / 'bild.png')
key = str(link / 'bild.png')
r, ev = bridge('batch', dict(files=[key], output=str(OUT / 'batch'), settings={},
                             per_photo={key: dict(corners=[[0, 0], [.5, 0], [.5, .5], [0, .5]], scale=1, mode='klassisch')}))
res = [e for e in ev if e['type'] == 'result']
pngs = sorted((OUT / 'batch').glob('01_*.png'))
print('B10 Exit', r.returncode, 'Ergebnis', bool(res), '| Ausgabe', Image.open(pngs[0]).size if pngs else None, '| erwartet ca. 500x400 (bei scale 1)')
r, ev = bridge('batch', dict(files=[str(real / 'bild.png')], output=str(OUT / 'batch2'), settings={},
                             per_photo={str(real / 'bild.png'): dict(corners=[[0, 0], [.5, 0], [.5, .5], [0, .5]], scale=1, mode='klassisch')}))
pngs = sorted((OUT / 'batch2').glob('01_*.png'))
print('B10 Gegenprobe ohne Link:', Image.open(pngs[0]).size if pngs else None)

# B12: 16-Bit-Grau und ICC
g = (np.tile(np.linspace(0, 65535, 512), (64, 1))).astype(np.uint16)
Image.fromarray(g).save(OUT / 'g16.png')
with Image.open(OUT / 'g16.png') as im: mode = im.mode
ri = np.asarray(read_image(OUT / 'g16.png')).astype(float)
print('B12 16-Bit-Grau: Modus', mode, 'read_image Mittel %.1f (erwartet ~127.5), Anteil 255: %.2f' % (ri.mean(), (ri == 255).mean()))
p3 = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'))  # Platzhalterprofil, Inhalt egal
icc = p3.tobytes()
Image.fromarray(np.random.default_rng(4).integers(0, 255, (400, 600, 3), dtype=np.uint8)).save(OUT / 'icc.jpg', icc_profile=icc)
from studio_backend import render_one
from adjustments import Settings
res = render_one(OUT / 'icc.jpg', OUT / 'icc_out.png', Settings(mode='klassisch', scale=1))
with Image.open(res['image']) as im:
    print('B12 ICC Quelle', len(icc), 'Byte | Ausgabe-PNG ICC', len(im.info.get('icc_profile') or b''), 'Byte')

# B15: freigegebenes Bild
prot = OUT / 'frei.png'
Image.fromarray(np.random.default_rng(5).integers(0, 255, (400, 600, 3), dtype=np.uint8)).save(prot)
fp = hashlib.sha256(read_image(prot).tobytes()).hexdigest()
fj = RES / 'Freigegebene_Bilder.json'; orig = fj.read_text()
try:
    fj.write_text(json.dumps(json.loads(orig) + [dict(image_sha256=fp)]))
    s = Settings(corners=[[.1, .1], [.9, .1], [.9, .9], [.1, .9]], retouch_strokes=[dict(points=[[.5, .5]], radius=.05)], values={'exposure': 50})
    res = render_one(prot, OUT / 'frei_out.png', s)
    same = open(res['image'], 'rb').read() == open(prot, 'rb').read()
    print('B15 Ausgabe', res['image'], 'identisch mit Quelle:', same, '| Warnungen', res['analysis']['warnings'],
          '| backend', res['analysis']['effective_backend'])
    r, ev = bridge('prepare', dict(source=str(prot), output=str(OUT / 'frei_prep.png'), settings=s.to_dict()))
    print('B15 prepare fuer freigegebenes Bild:', [e['type'] for e in ev], Image.open(OUT / 'frei_prep.png').size)
finally:
    fj.write_text(orig)
