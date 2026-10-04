"""Chat_Korrekturen.md Z.18: 'Mehrere Abzuege in einem Scan | Weisse Trenner erkennen; zusaetzliche Bildvorschlaege'.
Prueft: native Bruecke (batch + export) vs. alter CLI-Pfad graffiti.py."""
import sys, json, subprocess, os
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np
from PIL import Image
res = fresh_resources('split'); wd = res.parent
inp = wd / 'Scan'; inp.mkdir()
rng = np.random.default_rng(1)
a = rng.integers(20, 200, (1000, 3000, 3), dtype=np.uint8)
a[:, 980:1040] = 255; a[:, 1980:2040] = 255          # zwei weisse Trenner -> drei Abzuege
Image.fromarray(a).save(inp / 'scan_drei_abzuege.png')
src = str(inp / 'scan_drei_abzuege.png')
code, ev, err = bridge(res, 'batch', dict(files=[src], output=str(wd / 'Ordner_1'), settings=dict(mode='klassisch', scale=1)), wd)
res_ev = ev[-1]
print('native batch: exit', code, 'letztes Ereignis', res_ev['type'])
files = sorted(str(p.relative_to(wd / 'Ordner_1')) for p in (wd / 'Ordner_1').rglob('*') if p.is_file())
print('  Dateien:', files)
plan = json.load(open(wd / 'Ordner_1' / '01_scan_drei_abzuege.json'))
print('  panel_candidates im Plan:', plan.get('panel_candidates'))
print('  Warnung:', [w for w in plan['warnings'] if 'mehreren' in w])
print('  Bildvorschlaege erzeugt?', any('Bildvorschlag' in f for f in files))
code, ev, err = bridge(res, 'export', dict(source=src, output=str(wd / 'Foto_1' / 'scan.png'), settings=dict(mode='klassisch', scale=1)), wd)
files = sorted(str(p.relative_to(wd / 'Foto_1')) for p in (wd / 'Foto_1').rglob('*') if p.is_file())
print('native export: exit', code, ev[-1]['type'], 'Dateien:', files)
# Gegenprobe: alter CLI-Pfad (graffiti.main) erzeugt die Vorschlaege
r = subprocess.run([PY, str(res / 'graffiti.py'), '--input', str(inp), '--output', str(wd / 'CLI'), '--mode', 'klassisch', '--scale', '1'], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
files = sorted(str(p.relative_to(wd / 'CLI')) for p in (wd / 'CLI').rglob('*') if p.is_file() and 'Bildvorschlag' in str(p))
print('CLI graffiti.py: exit', r.returncode, 'Bildvorschlaege:', files)
