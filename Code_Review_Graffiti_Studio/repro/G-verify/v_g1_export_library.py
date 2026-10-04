"""G1: eigene Nachbildung von GraffitiStudio.swift:147-150 (exportLibrary) + echter Stapellauf ueber native_bridge."""
import copy, json, hashlib
from pathlib import Path
from PIL import Image
import numpy as np
from vcommon import *


def knobs(**kw):
    k = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', rotation=None,
             references=True, export='fotos', corners=None, regions=[], strokes=[])
    k.update(kw)
    return k


def to_json(k):  # KnobState.json (Swift Z.32-35)
    r = dict(values=k['values'], profile=k['profile'], mode=k['mode'], scale=k['scale'], geometry=k['geometry'],
             use_saved_retouches=k['references'], export=k['export'], glare_regions=k['regions'], retouch_strokes=k['strokes'])
    if k['rotation'] is not None: r['rotation'] = k['rotation']
    if k['corners'] is not None: r['corners'] = k['corners']
    return r


def export_library(selected, current, perPhoto):  # Swift Z.147-150, 1:1
    perPhoto = copy.deepcopy(perPhoto); perPhoto[selected] = copy.deepcopy(current)
    base = copy.deepcopy(current); base['corners'] = None; base['regions'] = []; base['strokes'] = []; base['rotation'] = None
    specific = {}
    for path, saved in perPhoto.items():
        m = copy.deepcopy(base); m['values'].update(saved['values'])
        m['corners'] = saved['corners']; m['regions'] = saved['regions']; m['strokes'] = saved['strokes']; m['rotation'] = saved['rotation']
        if saved['profile'] != 'auto': m['profile'] = saved['profile']
        if saved['mode'] != 'auto': m['mode'] = saved['mode']
        if saved['scale'] != 0: m['scale'] = saved['scale']
        if not saved['references']: m['references'] = False
        specific[path] = to_json(m)
    return to_json(base), specific


res = fresh_resources('g1')
inp = res.parent / 'in'; inp.mkdir()
printp = inp / 'abzug.png'; corners = make_print_on_table(printp)
recipes = json.loads((res / 'Fotorezepte.json').read_text())
recipes['abzug_synth'] = dict(corners=corners, rotate=90, glare_strength=.62, source_size=[900, 1200], image_sha256=fingerprint(printp))
(res / 'Fotorezepte.json').write_text(json.dumps(recipes))
refp = inp / 'referenz.png'
Image.fromarray(np.random.default_rng(3).integers(0, 255, (500, 700, 3), np.uint8)).save(refp)
cached = res / 'Referenzkorrekturen/Korrektur_X.png'; cached.parent.mkdir(exist_ok=True)
Image.new('RGB', (700, 500), (220, 20, 20)).save(cached)
refs = json.loads((res / 'Bekannte_Retuschen.json').read_text())
refs.append(dict(source_name='referenz.png', image_sha256=fingerprint(refp), cached='Referenzkorrekturen/Korrektur_X.png',
                 cached_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(), description='synth', generative_reconstruction=True))
(res / 'Bekannte_Retuschen.json').write_text(json.dumps(refs))
zug = inp / 'zug.png'; Image.new('RGB', (800, 500), (90, 110, 130)).save(zug)
files = [str(printp), str(refp), str(zug)]
visited = {str(printp): knobs(), str(refp): knobs()}

scen = {
    'Kontrolle (Zug gewaehlt, Standard)': knobs(mode='klassisch'),
    'Fall1: Zug gewaehlt, Papierkanten aus': knobs(mode='klassisch', geometry='aus'),
    'Fall2: Zug gewaehlt, nach Maske Uebernehmen (references=false)': knobs(mode='klassisch', references=False, corners=[[0, 0], [1, 0], [1, 1], [0, 1]]),
}
for i, (name, cur) in enumerate(scen.items()):
    base, specific = export_library(str(zug), cur, visited)
    out = res.parent / f'out{i}'
    code, ev, err = bridge(res, 'batch', dict(files=files, output=str(out), settings=base, per_photo=specific))
    print('==', name, '| exit', code, '| letztes Ereignis', ev[-1]['type'] if ev else None, err[-300:] if code else '')
    for f in sorted(out.glob('0*_*.json')):
        plan = json.loads(f.read_text())
        png = Image.open(f.with_suffix('.png'))
        tb, gr = table_fraction(png)
        print(f'   {f.stem}: settings.geometry={plan["settings"]["geometry"]} use_saved_retouches={plan["settings"]["use_saved_retouches"]} '
              f'Groesse={png.size} Tisch={tb} Nachbar={gr} executed[0]={plan["executed"][0][:60]!r}')
