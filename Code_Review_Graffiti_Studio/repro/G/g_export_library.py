"""LIES_MICH.txt:14 'gespeicherte Einzelwerte und Masken bleiben ihrem jeweiligen Foto zugeordnet'.
Python-Nachbildung von GraffitiStudio.swift:147-150 (exportLibrary) + Zeile 173 (closeMask setzt references=false),
danach ECHTER Stapellauf ueber native_bridge.py in einer Ressourcen-KOPIE."""
import sys, json, hashlib, copy, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np
from PIL import Image
res = fresh_resources('exportlib'); wd = res.parent
# Fotos: synthetischer Abzug IMG_4363 (Fingerabdruck in KOPIE eingetragen), bekannte KI-Referenz, Zugfoto
subprocess.run([PY, str(G / 'make_synth.py'), str(res), 'exif6'], check=True, capture_output=True)
subprocess.run([PY, str(G / 'make_synth.py'), str(res), 'inject'], check=True, capture_output=True)
rng = np.random.default_rng(7); Image.fromarray(rng.integers(30, 220, (600, 900, 3), dtype=np.uint8)).save(res / 'Fotos' / 'WFTPXN_synth.png')
Image.fromarray(np.random.default_rng(9).integers(30, 220, (700, 1000, 3), dtype=np.uint8)).save(res / 'Fotos' / 'zug.jpg')
code, out, err = py_in(res, f'from graffiti import read_image;from analysis import digest_image;from pathlib import Path;print(digest_image(read_image(Path({str(res / "Fotos/WFTPXN_synth.png")!r}))))')
(res / 'Referenzkorrekturen').mkdir(exist_ok=True); Image.new('RGB', (900, 600), (200, 40, 40)).save(res / 'Referenzkorrekturen/Korrektur_01.png')
rec = json.loads((res / 'Bekannte_Retuschen.json').read_text()); rec[0]['image_sha256'] = out.strip()
rec[0]['cached_sha256'] = hashlib.sha256((res / 'Referenzkorrekturen/Korrektur_01.png').read_bytes()).hexdigest()
(res / 'Bekannte_Retuschen.json').write_text(json.dumps(rec))
photos = [str(res / 'Fotos' / n) for n in ('IMG_4363.JPG', 'WFTPXN_synth.png', 'zug.jpg')]

def knob(**kw):  # KnobState() Standard, GraffitiStudio.swift:31
    k = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', rotation=None, references=True, export='fotos', corners=None, regions=[], strokes=[]); k.update(kw); return k
def as_json(k):  # KnobState.json, Swift:32-35
    r = dict(values=k['values'], profile=k['profile'], mode=k['mode'], scale=k['scale'], geometry=k['geometry'], use_saved_retouches=k['references'], export=k['export'], glare_regions=k['regions'], retouch_strokes=k['strokes'])
    if k['rotation'] is not None: r['rotation'] = k['rotation']
    if k['corners'] is not None: r['corners'] = k['corners']
    return r
def export_library(selected, knobs, perPhoto):  # Swift:147-150
    perPhoto = copy.deepcopy(perPhoto); perPhoto[selected] = knobs
    base = copy.deepcopy(knobs); base.update(corners=None, regions=[], strokes=[], rotation=None)
    specific = {}
    for path, saved in perPhoto.items():
        m = copy.deepcopy(base); m['values'].update(saved['values'])
        m.update(corners=saved['corners'], regions=saved['regions'], strokes=saved['strokes'], rotation=saved['rotation'])
        if saved['profile'] != 'auto': m['profile'] = saved['profile']
        if saved['mode'] != 'auto': m['mode'] = saved['mode']
        if saved['scale'] != 0: m['scale'] = saved['scale']
        if not saved['references']: m['references'] = False
        specific[path] = as_json(m)
    return as_json(base), specific

def run(label, selected, knobs):
    perPhoto = {photos[0]: knob(mode='klassisch'), photos[1]: knob(mode='klassisch')}  # beide vorher angesehen, nichts veraendert
    base, specific = export_library(selected, knobs, perPhoto)
    out = wd / ('Ordner_' + label)
    code, ev, err = bridge(res, 'batch', dict(files=photos, output=str(out), settings=base, per_photo=specific), wd)
    print(f'== {label}: Ergebnis {ev[-1]["type"]}')
    for n, p in enumerate(photos, 1):
        stem = p.rsplit('/', 1)[1].rsplit('.', 1)[0]
        plan = json.load(open(out / f'{n:02d}_{stem}.json'))
        im = Image.open(out / f'{n:02d}_{stem}.png').convert('RGB')
        h, s, v = [np.asarray(c).astype(float) for c in im.convert('HSV').split()]; hue = h / 255 * 360
        table = ((hue > 12) & (hue < 38) & (s > 80) & (v < 200)).mean()
        print(f'   {stem:14} per_photo.geometry={specific[p]["geometry"]:4} use_saved_retouches={specific[p]["use_saved_retouches"]!s:5} '
              f'Groesse={im.size} Tischanteil={table:.3f} executed[0]={plan["executed"][0][:60]!r}')

# Fall 1: Nutzer schaltet beim Zugfoto 'Automatische Papierkanten' aus (Swift:217) und exportiert den Ordner
run('Zug_ohne_Papierkanten', photos[2], knob(mode='klassisch', geometry='aus'))
# Fall 2: Nutzer setzt beim Zugfoto eine Maske; closeMask (Swift:173) setzt references=false; Ordner exportieren
run('Zug_mit_Maske', photos[2], knob(mode='klassisch', references=False, corners=[[0, 0], [1, 0], [1, 1], [0, 1]], strokes=[dict(points=[[.5, .5]], radius=.02)]))
# Kontrolle: gleicher Export mit Standardwerten am Zugfoto
run('Kontrolle', photos[2], knob(mode='klassisch'))
