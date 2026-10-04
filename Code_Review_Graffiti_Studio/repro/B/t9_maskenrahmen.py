"""Koordinatenrahmen Masken-Editor (native_bridge prepare) vs. Vorschau/Export (Settings.prepare_plan + apply_plan).
Abzug mit hinterlegtem Fotorezept (rotate=90) in der Testkopie Resources_t9.
Faelle:
  1) openMask bevor die erste Analyse fertig ist (plans[sel] fehlt) -> Vollbild-Ecken, rotation=nil
  2) danach Retuschstrich im Editor-Bild ueber einen Fleck gesetzt -> wo wirkt er im Export?
  3) (Variante) Geometrie-Schalter: 'aus' -> openMask -> Masken -> wieder 'auto'"""
import sys, os, json, hashlib, pathlib, subprocess, copy
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / 'Resources_t9'
if not RES.exists():
    import shutil; shutil.copytree(HERE / 'Resources', RES)
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image, ImageDraw
work = HERE / 'out_t9'; work.mkdir(exist_ok=True)

# Tisch (braun) mit Fotoabzug (hell), darauf ein schwarzer Fleck (zu retuschieren) und ein roter Orientierungspunkt
W, H = 1200, 1600
im = Image.new('RGB', (W, H), (120, 80, 40)); d = ImageDraw.Draw(im)
corners = [[.10, .10], [.85, .10], [.85, .90], [.10, .90]]
d.rectangle((int(.10 * W), int(.10 * H), int(.85 * W), int(.90 * H)), fill=(230, 230, 225))
d.ellipse((300, 300, 380, 380), fill=(0, 0, 0))        # Fleck auf dem Abzug
d.rectangle((900, 1300, 980, 1380), fill=(255, 0, 0))   # roter Punkt
src = work / 'P_abzug.png'; im.save(src)
from graffiti import read_image
digest = hashlib.sha256(read_image(src).tobytes()).hexdigest()
recipes = json.loads((RES / 'Fotorezepte.json').read_text())
recipes['P_abzug.png'] = dict(corners=corners, rotate=90, glare_strength=0.0, source_size=[W, H], image_sha256=digest)
(RES / 'Fotorezepte.json').write_text(json.dumps(recipes, indent=2))

import graffiti
from studio_backend import render_one
from adjustments import Settings
graffiti.SESSION.update(ai_available=False, ocr_available=False)

def swift(**kw):
    k = dict(values={}, profile='auto', mode='klassisch', scale=1, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])
    k.update(kw); return {x: y for x, y in k.items() if y is not None}

def bridge_prepare(knobs, out):
    req = work / 'req.json'; req.write_text(json.dumps(dict(source=str(src), output=str(out), settings=knobs)))
    r = subprocess.run([sys.executable, str(RES / 'native_bridge.py'), 'prepare', '--request', str(req)], capture_output=True, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
    assert '"result"' in r.stdout, r.stdout + r.stderr
    return np.array(Image.open(out).convert('RGB')).astype(int)

def blob(a):  # schwarzer Fleck: normierte Mitte
    m = a.max(axis=2) < 60; ys, xs = np.nonzero(m)
    return (xs.mean() / a.shape[1], ys.mean() / a.shape[0], m.sum()) if len(xs) else None

def red(a):
    m = (a[:, :, 0] > 200) & (a[:, :, 1] < 80); ys, xs = np.nonzero(m)
    return (round(xs.mean() / a.shape[1], 2), round(ys.mean() / a.shape[0], 2)) if len(xs) else None

def scenario(title, knobs_editor):
    mask_img = bridge_prepare(knobs_editor, work / 'maske.png')
    bx, by, _ = blob(mask_img)
    stroke = dict(points=[[bx, by]], radius=0.05)  # Nutzer uebermalt den Fleck im Editor-Bild
    k = dict(knobs_editor, retouch_strokes=[stroke], use_saved_retouches=False)
    r = render_one(src, work / 'export.png', Settings.from_dict(k), False)
    out = np.array(Image.open(r['image']).convert('RGB')).astype(int)
    b = blob(out)
    print(f'== {title}')
    print(f'   Editor-Bild {mask_img.shape[1]}x{mask_img.shape[0]}: Fleck bei ({bx:.2f},{by:.2f}), roter Punkt {red(mask_img)} -> Strich dort gesetzt')
    print(f'   Export      {out.shape[1]}x{out.shape[0]}: Fleck noch vorhanden: {b is not None and b[2] > 100}'
          f'{"" if b is None else f" bei ({b[0]:.2f},{b[1]:.2f}), {b[2]} px"}, roter Punkt {red(out)}, Tischfarbe-Anteil {((np.abs(out - [120, 80, 40]).sum(axis=2) < 40).mean()):.2f}')
    print('   executed:', r['analysis']['executed'][:1], '| preparation.rotate =', r['analysis']['preparation']['rotate'], 'corners =', r['analysis']['preparation']['corners'])

# Referenz: automatisches Rezept ohne Eingriff
r = render_one(src, work / 'auto.png', Settings.from_dict(swift()), False)
a = np.array(Image.open(r['image']).convert('RGB')).astype(int)
print(f'Auto-Rezept ohne Editor: {a.shape[1]}x{a.shape[0]}, Tischfarbe-Anteil {((np.abs(a - [120, 80, 40]).sum(axis=2) < 40).mean()):.2f}, roter Punkt {red(a)}')
plan_after_preview = r['analysis']

# 1/2) openMask bevor plans[sel] existiert: corners=Vollbild, rotation=nil
scenario('openMask vor fertiger Analyse (plans[sel] fehlt) + Strich im Editor', swift(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], rotation=None))
# Variante: openMask nach Analyse (Ecken/rotation aus Plan), dann Inspector 'Drehung: Automatisch' (rotation=nil), Editor erneut
scenario('openMask nach Analyse, dann Drehung "Automatisch", Editor erneut + Strich', swift(corners=plan_after_preview['preparation']['corners'], rotation=None))
# 3) Geometrie aus -> Vorschau -> openMask (Plan ohne preparation) -> Strich -> Geometrie wieder an
r_off = render_one(src, work / 'aus.png', Settings.from_dict(swift(geometry='aus')), True)
print('Vorschauplan mit Geometrie aus enthaelt preparation:', r_off['analysis'].get('preparation'))
scenario('Geometrie aus -> openMask -> Strich -> Geometrie wieder an', swift(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], rotation=None))
