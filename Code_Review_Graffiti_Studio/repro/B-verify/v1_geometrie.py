"""Eigene Gegenpruefung B2/B3/B4/B6/B7/B13/B14 (Bereich B). Arbeitet nur auf der Kopie ./Resources."""
import sys, json, copy, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
RES = HERE / 'Resources'
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image
from adjustments import Settings
from analysis import analyze, apply_plan
from photo_prepare import transform

FULL = [[0, 0], [1, 0], [1, 1], [0, 1]]
OUT = HERE / 'out_v1'; OUT.mkdir(exist_ok=True)

def swift_open_close(knobs, plan):
    """openMask (Z.171) + closeMask (Z.173) ohne Nutzereingriff nachgebildet."""
    k = dict(knobs)
    if k.get('corners') is None:
        prep = (plan or {}).get('preparation')
        if prep:
            k['corners'] = prep.get('corners'); k['rotation'] = prep.get('rotate')
        if k.get('corners') is None:
            k['corners'] = FULL
    k['use_saved_retouches'] = False
    return {kk: v for kk, v in k.items() if v is not None}

# ---------- B2-A: schwarze Balken ----------
rng = np.random.default_rng(1)
img = np.zeros((420, 1440, 3), np.uint8)
img[48:372] = rng.integers(60, 200, (324, 1440, 3), dtype=np.uint8)
im = Image.fromarray(img); src = OUT / 'balken.png'; im.save(src)
plan = analyze(im, src, ocr=False)
p0, _ = Settings().prepare_plan(plan); a0, n0 = apply_plan(im, p0)
s1 = Settings.from_dict(swift_open_close({}, p0))
p1, _ = s1.prepare_plan(plan); a1, n1 = apply_plan(im, p1)
print('B2-A border_crop im Plan:', plan.get('border_crop'))
print('B2-A vorher', a0.size, n0, '| nach Editor+Uebernehmen', a1.size, n1)
p2, _ = Settings(rotation=0).prepare_plan(plan); a2, n2 = apply_plan(im, p2)
print('B2-A Inspector Drehung 0 Grad:', a2.size, n2)

# ---------- B2-B: OCR-Drehung (Plan wie analysis.py:122) ----------
im2 = Image.fromarray(rng.integers(0, 255, (1000, 667, 3), dtype=np.uint8))
plan_b = analyze(im2, OUT / 'hoch.png', ocr=False); plan_b['rotation'] = 90
q0, _ = Settings().prepare_plan(plan_b); b0, m0 = apply_plan(im2, q0)
q1, _ = Settings.from_dict(swift_open_close({}, q0)).prepare_plan(plan_b); b1, m1 = apply_plan(im2, q1)
print('B2-B vorher', b0.size, m0, '| nachher', b1.size, m1)

# ---------- B2-C + B14: cached_correction ----------
plan_c = copy.deepcopy(plan_b); plan_c.pop('rotation')
plan_c['cached_correction'] = dict(cached='x.png', cached_sha256='0')
plan_c['warnings'].append('Die hinterlegte Einzelretusche enthält KI-rekonstruierte Details.')
r0, _ = Settings().prepare_plan(plan_c)
r1, _ = Settings.from_dict(swift_open_close({}, r0)).prepare_plan(plan_c)
r2, _ = Settings(corners=FULL, use_saved_retouches=True).prepare_plan(plan_c)
print('B2-C vorher cached_correction:', 'cached_correction' in r0, '| nach Editor:', 'cached_correction' in r1,
      '| Schalter wieder an (corners bleibt):', 'cached_correction' in r2)
print('B14 KI-Warnung nach Wegfall:', any('KI-rekonstruiert' in w for w in r1['warnings']))

# ---------- B3/B4: Fotorezept mit rotate 90 ----------
H, W = 1600, 1200
base = np.full((H, W, 3), (150, 90, 40), np.uint8)              # Tisch braun
x0, y0, x1, y1 = int(.10 * (W - 1)), int(.10 * (H - 1)), int(.90 * (W - 1)), int(.85 * (H - 1))
base[y0:y1, x0:x1] = (225, 225, 225)                              # Abzug hell
fx, fy = x0 + 80, y0 + 60
base[fy - 15:fy + 15, fx - 15:fx + 15] = (0, 0, 0)               # Fleck
photo = Image.fromarray(base); psrc = OUT / 'abzug.png'; photo.save(psrc)
rec_corners = [[.10, .10], [.90, .10], [.90, .85], [.10, .85]]
plan_r = analyze(photo, psrc, ocr=False)
plan_r['preparation'] = dict(corners=rec_corners, rotate=90, glare_strength=0.0)
plan_r.pop('border_crop', None)
t0, _ = Settings().prepare_plan(plan_r); o0, _ = apply_plan(photo, t0)
# B3: openMask ohne Plan -> Vollbild-Ecken, rotation nil
t1, _ = Settings(corners=FULL, use_saved_retouches=False).prepare_plan(plan_r); o1, _ = apply_plan(photo, t1)
def table(img):
    a = np.asarray(img).astype(int); return float(((abs(a[..., 0] - 150) < 8) & (abs(a[..., 1] - 90) < 8)).mean())
print('B3 Automatik', o0.size, 'Tischanteil %.2f' % table(o0), '| Editor vor Analyse', o1.size, 'Tischanteil %.2f' % table(o1),
      'rotate', t1['preparation']['rotate'], 'corners', t1['preparation']['corners'])

# B4: rotation=None, corners=Rezept -> prepare-Bild (native_bridge) vs Export
def bridge_prepare(settings):
    req = OUT / 'req.json'; out = OUT / 'prep.png'
    req.write_text(json.dumps(dict(source=str(psrc), output=str(out), settings=settings)))
    r = subprocess.run([sys.executable, str(RES / 'native_bridge.py'), 'prepare', '--request', str(req)], capture_output=True, text=True)
    return r, (Image.open(out).convert('RGB') if r.returncode == 0 else None)
def find_spot(img):
    a = np.asarray(img).astype(int); m = (a.sum(axis=2) < 60)
    if not m.any(): return None
    ys, xs = np.nonzero(m); return round(xs.mean() / a.shape[1], 3), round(ys.mean() / a.shape[0], 3), int(m.sum())
for label, sett in [('(a) corners=Rezept, rotation=None', dict(corners=rec_corners)),
                    ('(b/c) corners=Vollbild, rotation=None', dict(corners=FULL))]:
    r, prep_img = bridge_prepare(sett)
    spot = find_spot(prep_img)
    stroke = [dict(points=[[spot[0], spot[1]]], radius=.05)]
    s = Settings(**sett, retouch_strokes=stroke, use_saved_retouches=False)
    pl, _ = s.prepare_plan(plan_r); out_img, _ = apply_plan(photo, pl)
    print('B4', label, '| Editorbild', prep_img.size, 'Fleck', spot[:2], '| Export', out_img.size, 'rotate', pl['preparation']['rotate'],
          '| Fleck nach Retusche noch da:', find_spot(out_img))
# Gegenprobe: rotation explizit 90 -> passt
sett = dict(corners=rec_corners, rotation=90); r, prep_img = bridge_prepare(sett); spot = find_spot(prep_img)
pl, _ = Settings(**sett, retouch_strokes=[dict(points=[[spot[0], spot[1]]], radius=.05)]).prepare_plan(plan_r)
print('B4 Gegenprobe rotation=90 explizit: Fleck nach Retusche:', find_spot(apply_plan(photo, pl)[0]))
# B4 (d): Rezept mit glare_regions, Nutzer-Ecken ohne eigene Masken
plan_d = copy.deepcopy(plan_r); plan_d['preparation']['glare_regions'] = [[.1, .1, .3, .3]]
pd, _ = Settings(corners=FULL).prepare_plan(plan_d)
print('B4 (d) Rezeptmasken bleiben bei neuen Ecken erhalten:', pd['preparation'].get('glare_regions'))

# ---------- B6 ----------
wall = Image.fromarray(np.clip(rng.normal(120, 20, (600, 800, 3)), 0, 255).astype(np.uint8))
a = np.asarray(wall).copy(); a[200:400, 300:500] = np.clip(a[200:400, 300:500].astype(int) + 70, 0, 255); wall = Image.fromarray(a)
wplan = analyze(wall, OUT / 'wand.png', ocr=False); wplan['preparation'] = None; wplan.pop('border_crop', None)
for g in (None, 50):
    vals = {} if g is None else {'glare': g}
    pp, ctrl = Settings(values=vals, corners=FULL, glare_regions=[[.35, .3, .65, .7]]).prepare_plan(wplan)
    out_img, _ = apply_plan(wall, pp)
    diff = np.abs(np.asarray(out_img).astype(int) - np.asarray(wall).astype(int))[200:400, 300:500].mean()
    print('B6 Wand Regler', 'Auto' if g is None else g, 'glare=', ctrl['glare'], 'Aenderung im Rechteck %.2f' % diff,
          'Warnungen Reflex:', [w for w in pp['warnings'] if 'Reflexregler' in w])
haze = np.asarray(wall).astype(np.float32) * .6 + 90
hz = Image.fromarray(haze.astype(np.uint8))
cfg = dict(corners=FULL, rotate=0, glare_strength=.6)
o_glob = transform(hz, cfg); o_reg = transform(hz, dict(cfg, glare_regions=[[.0, .0, .1, .1]]))
outside = (slice(300, 600), slice(400, 800))
print('B6 Abzug: Mittel ausserhalb Original %.1f | ohne Rechteck %.1f | mit kleinem Rechteck %.1f' % (
    np.asarray(hz)[outside].mean(), np.asarray(o_glob)[outside].mean(), np.asarray(o_reg)[outside].mean()))

# ---------- B7 ----------
asym = np.zeros((300, 400, 3), np.uint8); asym[10:60, 10:80] = (255, 0, 0); asym[130:170, 350:395] = (0, 0, 255)
A = Image.fromarray(asym)
for name, c in [('TL,TR,BR,BL', FULL), ('TL,BL,BR,TR', [[0, 0], [0, 1], [1, 1], [1, 0]]), ('TR,BR,BL,TL', [[1, 0], [1, 1], [0, 1], [0, 0]])]:
    try:
        Settings(corners=c); out_img = transform(A, dict(corners=c, rotate=0))
        o = np.asarray(out_img); same = o.shape == asym.shape and np.abs(o.astype(int) - asym).max() < 30
        transp = o.shape[:2] == asym.shape[1::-1] and np.abs(o.astype(int) - asym.transpose(1, 0, 2)).max() < 30
        print('B7', name, 'Settings ok, Ausgabe', out_img.size, 'identisch', same, 'transponiert', transp)
    except ValueError as e:
        print('B7', name, 'abgewiesen:', e)
mir = transform(A, dict(corners=[[0, 0], [0, 1], [1, 1], [1, 0]], rotate=0))
print('B7 gespiegelt + Drehung = Original?', [np.asarray(mir.rotate(r, expand=True)).shape == asym.shape and
       np.abs(np.asarray(mir.rotate(r, expand=True)).astype(int) - asym).max() < 30 for r in (0, 90, 180, 270)])
