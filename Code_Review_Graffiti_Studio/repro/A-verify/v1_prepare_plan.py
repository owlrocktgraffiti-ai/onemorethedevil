"""Gegenpruefung A2, A3, A4, A15, A17 direkt an Settings.prepare_plan / transform (ohne Fotos).
Plaene werden synthetisch so gebaut, wie analyze() sie liefert (Rezept IMG_4363: rotate 90, glare .62)."""
import sys, json, copy
from pathlib import Path
R = Path(__file__).resolve().parent / 'Resources'
sys.path.insert(0, str(R))
import numpy as np
from PIL import Image
from adjustments import Settings
from photo_prepare import transform

def base_plan(prep=None, **extra):
    p = dict(version='4.0', image_sha256='x', features={'cast_suspected': False}, actions=[], warnings=[],
             preparation=copy.deepcopy(prep), look='kraeftig', scale=1, white_balance_rgb=[1, 1, 1], color_factor=1.0)
    p.update(extra)
    return p

RECIPE = dict(corners=[[0.012, 0.034], [0.847, 0.039], [0.856, 0.927], [0.087, 0.943]], rotate=90, glare_strength=0.62)
CACHED = {'cached': 'Referenzkorrekturen/Korrektur_02.png'}

print('=== A2: Swift-exportLibrary-Merge nachgebildet (Zeilen 147-149) ===')
def swift_merge(selected_knobs, saved):
    base = dict(selected_knobs); base.update(corners=None, glare_regions=[], retouch_strokes=[], rotation=None)
    merged = dict(base); merged['values'] = {**base['values'], **saved['values']}
    for k in ('corners', 'glare_regions', 'retouch_strokes', 'rotation'): merged[k] = saved[k]
    if saved['profile'] != 'auto': merged['profile'] = saved['profile']
    if saved['mode'] != 'auto': merged['mode'] = saved['mode']
    if saved['scale'] != 0: merged['scale'] = saved['scale']
    if not saved['use_saved_retouches']: merged['use_saved_retouches'] = False
    return base, merged
default = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', rotation=None, use_saved_retouches=True,
               export='fotos', corners=None, glare_regions=[], retouch_strokes=[])
for label, sel in [('ausgewaehlt: Papierkanten aus', dict(default, geometry='aus')),
                   ('ausgewaehlt: references=false (nach closeMask)', dict(default, use_saved_retouches=False))]:
    base, merged = swift_merge(sel, dict(default))   # anderes, besuchtes Foto mit Standardwerten
    for name, s in [('nicht besucht (Basis)', base), ('besucht, eigene Werte auto/true', merged)]:
        st = Settings.from_dict(s)
        plan, _ = st.prepare_plan(base_plan(RECIPE, cached_correction=CACHED))
        print(f'  {label} | {name}: geometry={s["geometry"]} refs={s["use_saved_retouches"]} -> preparation={"ja" if plan.get("preparation") else "NEIN"}, cached_correction={"ja" if "cached_correction" in plan else "NEIN"}')

print('=== A3: openMask ohne Plan -> Vollbild-Ecken, rotation nil, closeMask references=false ===')
full = [[0, 0], [1, 0], [1, 1], [0, 1]]
for label, plan_in in [('Rezeptfoto (rotate 90)', base_plan(RECIPE)),
                       ('Wandfoto mit OCR-Drehung+Randbalken', base_plan(None, rotation=90, border_crop=[100, 150, 1300, 850])),
                       ('Foto mit Referenzretusche', base_plan(None, cached_correction=CACHED))]:
    auto, _ = Settings().prepare_plan(plan_in)
    man, _ = Settings(corners=full, use_saved_retouches=False).prepare_plan(plan_in)
    keys = lambda p: {k: p.get(k) for k in ('rotation', 'border_crop')} | {'cached': 'cached_correction' in p, 'prep_corners': (p.get('preparation') or {}).get('corners'), 'prep_rotate': (p.get('preparation') or {}).get('rotate')}
    print(f'  {label}\n    Automatik : {keys(auto)}\n    nach Editor: {keys(man)}')
    man2, _ = Settings(corners=full, use_saved_retouches=True).prepare_plan(plan_in)
    print(f'    nur Ecken, Schalter an: cached={"cached_correction" in man2}')

print('=== A4: prepare (native_bridge:36) vs Render (prepare_plan) bei rotation=None ===')
img = Image.new('RGB', (900, 1200), (128, 128, 128))
st = Settings(corners=full, retouch_strokes=[{'points': [[0.1, 0.1]], 'radius': 0.02}])
prep_cfg = dict(corners=st.corners or full, rotate=st.rotation or 0, glare_strength=0)
render_plan, _ = st.prepare_plan(base_plan(RECIPE))
print('  Maskenbild:', transform(img, prep_cfg).size, 'rotate', prep_cfg['rotate'])
print('  Render    :', transform(img, dict(corners=render_plan['preparation']['corners'], rotate=render_plan['preparation']['rotate'])).size, 'rotate', render_plan['preparation']['rotate'])
# Wo landet ein Strich an Maskenbild-Position (0.1,0.1)? Marker im Original oben links, Strich wird nach Drehung angewandt
marker = Image.new('RGB', (900, 1200), (128, 128, 128)); marker.paste((255, 0, 0), (60, 90, 120, 150))  # bei (0.1,0.1) im ungedrehten Bild
rot = transform(marker, dict(corners=full, rotate=90))
a = np.array(rot); ys, xs = np.where(a[:, :, 0] > 200)
print(f'  Markierte Stelle (0.1,0.1) im Maskenbild liegt im gedrehten Render bei x={xs.mean()/a.shape[1]:.2f}, y={ys.mean()/a.shape[0]:.2f}; Strich wirkt aber bei (0.10,0.10)')

print('=== A15: Reflexbereich ohne Abzug, Regler Auto ===')
st = Settings(glare_regions=[[0.2, 0.2, 0.6, 0.6]])
plan, controls = st.prepare_plan(base_plan(None))
print('  controls.glare =', controls['glare'], '| preparation.glare_strength =', plan['preparation']['glare_strength'], '| Warnungen:', plan['warnings'])
rng = np.random.default_rng(1); noisy = Image.fromarray(rng.integers(60, 255, (400, 600, 3), dtype=np.uint8))
with_r = np.array(transform(noisy, plan['preparation'])).astype(int)
without = np.array(transform(noisy, dict(corners=full, rotate=0, glare_strength=0))).astype(int)
print('  max. Pixelabweichung mit/ohne Bereich:', np.abs(with_r - without).max())
plan50, _ = Settings(values={'glare': 50}, glare_regions=[[0.2, 0.2, 0.6, 0.6]]).prepare_plan(base_plan(None))
print('  Regler 50 %: max. Abweichung:', np.abs(np.array(transform(noisy, plan50['preparation'])).astype(int) - without).max())

print('=== A17: JSON fuer Foto ohne Abzug ===')
plan, _ = Settings().prepare_plan(base_plan(None))
print('  ', [s for s in json.dumps(plan, ensure_ascii=False).split(', ') if 'preparation' in s])
