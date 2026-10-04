"""Prueft einzelne Doku-Aussagen ausfuehrend (nur Kopien)."""
import sys, json, hashlib, csv
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np
from PIL import Image

res = fresh_resources('doc'); wd = res.parent
rng = np.random.default_rng(3)
Image.fromarray(rng.integers(30, 220, (700, 1000, 3), dtype=np.uint8)).save(wd / 'zug.jpg')

print('(a) Werden Masken zu Fotorezepten? (Chat_Korrekturen.md:30)')
h0 = hashlib.sha256((res / 'Fotorezepte.json').read_bytes()).hexdigest()
masks = dict(corners=[[0.05, 0.05], [0.95, 0.05], [0.95, 0.95], [0.05, 0.95]], rotation=90, glare_regions=[[0.2, 0.2, 0.4, 0.4]],
             retouch_strokes=[dict(points=[[0.5, 0.5], [0.6, 0.5]], radius=0.02)], use_saved_retouches=False, values=dict(glare=50))
for cmd, req in [('preview', dict(source=str(wd / 'zug.jpg'), output=str(wd / 'p.png'), settings=masks)),
                 ('export', dict(source=str(wd / 'zug.jpg'), output=str(wd / 'Foto_x' / 'zug.png'), settings=masks)),
                 ('batch', dict(files=[str(wd / 'zug.jpg')], output=str(wd / 'Ordner_x'), settings=masks))]:
    code, ev, err = bridge(res, cmd, req, wd); print('   ', cmd, ev[-1]['type'])
h1 = hashlib.sha256((res / 'Fotorezepte.json').read_bytes()).hexdigest()
print('    Fotorezepte.json unveraendert:', h0 == h1)
code, ev, err = bridge(res, 'preview', dict(source=str(wd / 'zug.jpg'), output=str(wd / 'p2.png'), settings={}), wd)
print('    Folgevorschau ohne Masken im Request: Ausgabegroesse', Image.open(ev[-1]['result']['image']).size,
      '| executed:', ev[-1]['result']['analysis']['executed'][:1])

print('(c) "preparation" im Vorschau-JSON fuer unbekanntes Foto (GraffitiStudio.swift:132 prueft != nil)')
raw = [l for l in open(ev[-1]['result']['plan']).read().splitlines() if '"preparation"' in l]
print('    Plan-Datei:', raw, '| im result-Ereignis:', repr(ev[-1]['result']['analysis'].get('preparation', 'SCHLUESSEL FEHLT')))

print('(d) Regler_Schema.json == adjustments.schema()?')
code, out, err = py_in(res, 'import json;from adjustments import schema;from pathlib import Path;print(json.loads(Path(sys.path[0],"Regler_Schema.json").read_text())==schema())')
print('   ', out.strip(), err.strip()[-200:])

print('(e) Rezepte/*.json mit Settings.from_dict ladbar?')
code, out, err = py_in(res, 'import json;from adjustments import Settings;from pathlib import Path\nfor p in sorted(Path(sys.path[0],"Rezepte").glob("*.json")):\n Settings.from_dict(json.loads(p.read_text()));print(p.name,"ok")')
print('   ', out.replace('\n', ' '), err.strip()[-300:])

print('(g) Ohne tkinter (Homebrew python@3.14 ohne python-tk@3.14):')
code, ev, err = bridge(res, 'preview', dict(source=str(wd / 'zug.jpg'), output=str(wd / 'p3.png'), settings={}), wd,
                       env_extra=dict(PYTHONPATH=str(G / 'no_tk')))
print('    exit', code, 'Ereignisse', [e['type'] for e in ev], '| stderr-Ende:', err.strip().splitlines()[-1] if err.strip() else '')
