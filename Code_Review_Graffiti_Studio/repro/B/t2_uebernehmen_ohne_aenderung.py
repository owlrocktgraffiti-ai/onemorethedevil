"""Hinweis 2: 'Ecken & Maske bearbeiten…' oeffnen und sofort 'Übernehmen' (ohne jede Aenderung).
Simuliert exakt die Swift-Logik:
  openMask(): wenn knobs.corners==nil -> corners/rotation aus plans[sel]['preparation'], sonst Vollbild-Ecken
  closeMask(): knobs.references=false
und vergleicht render_one (Vorschau-Weg) vorher/nachher an drei synthetischen Fotos:
  A) Panorama mit gleichmaessigen schwarzen Balken (border_crop)
  B) Foto, das die (hier per Stub simulierte) lokale Texterkennung sicher als 90° gedreht erkennt (plan['rotation'])
  C) Foto mit exakt zugeordneter hinterlegter Referenzkorrektur (cached_correction, generativ)
Laeuft gegen die Testkopie Resources_t2 (mit Stub engine/orientation und Testeintrag in Bekannte_Retuschen.json)."""
import sys, os, json, hashlib, pathlib, copy
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / 'Resources_t2'
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image, ImageDraw
work = HERE / 'out_t2'; work.mkdir(exist_ok=True)

def swift_default():
    return dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])

def open_and_accept(knobs, plan):
    k = copy.deepcopy(knobs)
    if k.get('corners') is None:
        prep = plan.get('preparation') if isinstance(plan.get('preparation'), dict) else None
        if prep:
            k['corners'] = prep.get('corners');
            if isinstance(prep.get('rotate'), int): k['rotation'] = prep['rotate']
        if k.get('corners') is None: k['corners'] = [[0, 0], [1, 0], [1, 1], [0, 1]]
    k['use_saved_retouches'] = False  # closeMask
    return k

def marker(path):
    a = np.array(Image.open(path).convert('RGB')).astype(int)
    m = (a[:, :, 0] > 200) & (a[:, :, 1] < 80) & (a[:, :, 2] < 80)
    ys, xs = np.nonzero(m)
    return (round(xs.mean() / a.shape[1], 2), round(ys.mean() / a.shape[0], 2)) if len(xs) else None

# --- Testbilder
srcA = work / 'A_panorama_balken.png'
a = np.full((700, 2400, 3), 120, np.uint8); a[:80] = 0; a[-80:] = 0; a[200:300, 100:300] = (255, 0, 0)
Image.fromarray(a).save(srcA)
srcB = work / 'B_hochformat_ocr90.png'
b = np.full((1200, 800, 3), 140, np.uint8); b[50:200, 50:250] = (255, 0, 0); Image.fromarray(b).save(srcB)
srcC = work / 'C_referenz.png'
c = np.full((800, 1200, 3), 90, np.uint8); c[100:200, 100:300] = (255, 0, 0); Image.fromarray(c).save(srcC)
# hinterlegte Referenzkorrektur fuer C (deutlich erkennbar: gruen)
(RES / 'Referenzkorrekturen').mkdir(exist_ok=True)
ref = RES / 'Referenzkorrekturen' / 'Test_C.png'; Image.new('RGB', (1200, 800), (0, 200, 0)).save(ref)
from graffiti import read_image
digestC = hashlib.sha256(read_image(srcC).tobytes()).hexdigest()
records = json.loads((RES / 'Bekannte_Retuschen.json').read_text())
records = [r for r in records if r.get('source_name') != 'C_referenz.png']
records.append(dict(source_name='C_referenz.png', image_sha256=digestC, cached='Referenzkorrekturen/Test_C.png', cached_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(), description='Test', generative_reconstruction=True))
(RES / 'Bekannte_Retuschen.json').write_text(json.dumps(records, indent=2))

import graffiti
from studio_backend import render_one
from adjustments import Settings
for label, src, ocr in [('A Balken', srcA, '0'), ('B OCR-Drehung', srcB, '90'), ('C Referenzkorrektur', srcC, '0')]:
    os.environ['OCR_ROTATE'] = ocr
    graffiti.SESSION.update(ai_available=False, ocr_available=True)
    k0 = swift_default()
    r0 = render_one(src, work / f'{src.stem}_vorher.png', Settings.from_dict(k0), True)
    plan = r0['analysis']  # das speichert Swift in plans[selected]
    k1 = open_and_accept(k0, plan)
    graffiti.SESSION.update(ai_available=False, ocr_available=True)
    r1 = render_one(src, work / f'{src.stem}_nachher.png', Settings.from_dict(k1), True)
    def info(r):
        im = Image.open(r['image']); arr = np.array(im.convert('RGB')).astype(int)
        return f"{im.size[0]}x{im.size[1]}, Marker@{marker(r['image'])}, Mittel(R,G,B)={tuple(arr.mean(axis=(0,1)).round(0).astype(int))}, Referenz-Warnung={'KI-rekonstruierte' in ' '.join(r['analysis']['warnings'])}, executed={r['analysis']['executed'][:1]}"
    print(f'== {label}: Swift-Knobs nach Übernehmen: corners={k1["corners"]} rotation={k1.get("rotation")} use_saved_retouches={k1["use_saved_retouches"]}')
    print('   vorher :', info(r0))
    print('   nachher:', info(r1))

# Danach im Inspector „Bekannte Einzelretuschen“ wieder einschalten (corners bleiben gesetzt):
os.environ['OCR_ROTATE'] = '0'
graffiti.SESSION.update(ai_available=False, ocr_available=True)
k2 = dict(open_and_accept(swift_default(), {}), use_saved_retouches=True)
r2 = render_one(srcC, work / 'C_schalter_wieder_an.png', Settings.from_dict(k2), True)
arr = np.array(Image.open(r2['image']).convert('RGB')).astype(int)
print('== C, Schalter „Bekannte Einzelretuschen“ wieder an: Mittel(R,G,B)=', tuple(arr.mean(axis=(0, 1)).round(0).astype(int)), '| executed:', r2['analysis']['executed'][:1])
