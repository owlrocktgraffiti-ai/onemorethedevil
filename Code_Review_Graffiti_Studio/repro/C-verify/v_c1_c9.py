"""Gegenpruefung C1 (exportLibrary-Request) und C9 (Referenzwarnung nach Abschalten).
Eigene Nachbildung von GraffitiStudio.swift:147-150 und KnobState.json (Zeile 31-35)."""
import sys, json, copy, hashlib, shutil
from pathlib import Path
HERE = Path(__file__).resolve().parent
RES = HERE / 'Resources'
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image
from adjustments import Settings

def knob(**kw):
    k = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', rotation=None,
             references=True, export='fotos', corners=None, regions=[], strokes=[])
    k.update(kw); return k

def to_json(k):
    r = dict(values=k['values'], profile=k['profile'], mode=k['mode'], scale=k['scale'], geometry=k['geometry'],
             use_saved_retouches=k['references'], export=k['export'], glare_regions=k['regions'], retouch_strokes=k['strokes'])
    if k['rotation'] is not None: r['rotation'] = k['rotation']
    if k['corners'] is not None: r['corners'] = k['corners']
    return r

def export_library(knobs, selected, perPhoto, photos):
    perPhoto = dict(perPhoto); perPhoto[selected] = knobs
    base = copy.deepcopy(knobs); base.update(corners=None, regions=[], strokes=[], rotation=None)
    specific = {}
    for path, saved in perPhoto.items():
        m = copy.deepcopy(base); m['values'] = {**m['values'], **saved['values']}
        m['corners'] = saved['corners']; m['regions'] = saved['regions']; m['strokes'] = saved['strokes']; m['rotation'] = saved['rotation']
        if saved['profile'] != 'auto': m['profile'] = saved['profile']
        if saved['mode'] != 'auto': m['mode'] = saved['mode']
        if saved['scale'] != 0: m['scale'] = saved['scale']
        if not saved['references']: m['references'] = False
        specific[path] = to_json(m)
    return dict(files=photos, settings=to_json(base), per_photo=specific)

def effective(req, path):
    return Settings.from_dict(req['per_photo'].get(path, req['settings']))

# synthetischer Plan wie analyze() ihn fuer einen Abzug mit Fotorezept bzw. ein Referenzfoto liefert
PLAN_ABZUG = dict(preparation=dict(corners=[[.1, .1], [.9, .1], [.9, .9], [.1, .9]], rotate=90, glare_strength=.5),
                  features={}, warnings=[], look='kraeftig')
PLAN_WAND = dict(preparation=None, cached_correction={'cached': 'x'}, features={}, warnings=['Die hinterlegte Einzelretusche enthält KI-rekonstruierte Details.'], look='kraeftig')
photos = ['/F/IMG_4363.JPG', '/F/WFTPXN.jpg', '/F/C.jpg']

def show(title, req):
    a = effective(req, photos[0]).prepare_plan(PLAN_ABZUG)[0]
    b = effective(req, photos[1]).prepare_plan(PLAN_WAND)[0]
    print(f'{title}: Abzug preparation={"ja (rotate %s)" % a["preparation"]["rotate"] if a.get("preparation") else "ENTFERNT"}'
          f' | Wand cached_correction={"ja" if "cached_correction" in b else "ENTFERNT"} | glare Abzug={a["controls"]["glare"]}')

# 1 Normalfall
show('1 C gewaehlt, alles auto', export_library(knob(), photos[2], {}, photos))
# 2 (a) C hat Papierkanten aus
show('2 C geometry=aus', export_library(knob(geometry='aus'), photos[2], {}, photos))
# 3 (a) A besucht, auto; C aus
show('3 A besucht(auto), C geometry=aus', export_library(knob(geometry='aus'), photos[2], {photos[0]: knob()}, photos))
# 4 (a umgekehrt) A bewusst aus, C gewaehlt auto
r = export_library(knob(), photos[2], {photos[0]: knob(geometry='aus')}, photos)
print('4 A geometry=aus gewaehlt, C auto: gesendet A geometry =', r['per_photo'][photos[0]]['geometry'])
# 5 (b) closeMask auf C -> references=false
show('5 C nach closeMask (references=false, corners gesetzt)', export_library(knob(references=False, corners=[[0, 0], [1, 0], [1, 1], [0, 1]]), photos[2], {}, photos))
# 6 (c) A besucht auto; C explizit glare=0
show('6 A besucht(auto), C glare=0', export_library(knob(values={'glare': 0}), photos[2], {photos[0]: knob()}, photos))

# ---------------- C9: echte analyze() mit injiziertem Referenzeintrag -----------------
print('\n--- C9 ---')
from analysis import analyze, digest_image
work = HERE / 'work_c9'; shutil.rmtree(work, ignore_errors=True); work.mkdir()
rng = np.random.default_rng(1)
a = (rng.normal(90, 25, (900, 1200, 3))).clip(0, 255).astype(np.uint8)
yy, xx = np.mgrid[:900, :1200]; d = np.hypot(yy - 450, xx - 600)
a[d < 120] = 255; m = (d >= 120) & (d < 220); a[m] = np.clip(a[m] + (220 - d[m, None]) * 1.6, 0, 255).astype(np.uint8)
src = work / 'blitz.jpg'; Image.fromarray(a).save(src, quality=95)
from graffiti import read_image
img = read_image(src); fp = digest_image(img)
retfile = RES / 'Bekannte_Retuschen.json'; orig_ret = retfile.read_text()
cached = RES / 'Referenzkorrekturen' / 'test_c9.png'; cached.parent.mkdir(exist_ok=True); img.save(cached)
try:
    plan0 = analyze(img, src, ocr=False)
    print('ohne Eintrag: warnings =', plan0['warnings'])
    rec = dict(source_name='blitz.jpg', image_sha256=fp, cached='Referenzkorrekturen/test_c9.png',
               cached_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(), generative_reconstruction=True)
    retfile.write_text(json.dumps(json.loads(orig_ret) + [rec]))
    plan1 = analyze(img, src, ocr=False)
    for label, s in [('Referenz an', Settings()), ('Referenz aus', Settings(use_saved_retouches=False)),
                     ('Retuschstrich', Settings(retouch_strokes=[dict(points=[[.5, .5]], radius=.02)]))]:
        p, _ = s.prepare_plan(plan1)
        print(f'{label}: cached_correction={"cached_correction" in p} | warnings={p["warnings"]}')
finally:
    retfile.write_text(orig_ret); cached.unlink(missing_ok=True)
