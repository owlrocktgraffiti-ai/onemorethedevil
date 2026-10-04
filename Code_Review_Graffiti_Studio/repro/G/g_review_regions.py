"""Chat_Korrekturen.md:13 'Kamerablitz / helle Reflexflecken ... markierte Bereiche im Vergleich, Befund im Analyseplan'.
Native Bruecke (batch) vs. alter CLI-Pfad graffiti.py: Sind die Verdachtsbereiche im Vergleichsbild markiert?"""
import sys, json, subprocess, os
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np, cv2
from PIL import Image
res = fresh_resources('review'); wd = res.parent; inp = wd / 'in'; inp.mkdir()
rng = np.random.default_rng(2)
a = rng.integers(40, 110, (800, 1200, 3), dtype=np.uint8)
cv2.circle(a, (600, 400), 70, (255, 255, 255), -1)          # zentraler Blitzfleck, ausgebrannt
Image.fromarray(a).save(inp / 'blitz.jpg', quality=95)
def yellow(p):
    v = np.asarray(Image.open(p).convert('RGB')).astype(int)
    return int(((abs(v[..., 0] - 255) < 40) & (abs(v[..., 1] - 206) < 40) & (v[..., 2] < 110)).sum())
code, ev, err = bridge(res, 'batch', dict(files=[str(inp / 'blitz.jpg')], output=str(wd / 'Ordner'), settings=dict(mode='klassisch', scale=1)), wd)
plan = json.load(open(wd / 'Ordner' / '01_blitz.json'))
print('native batch:', ev[-1]['type'], '| review_regions im Plan:', plan.get('review_regions'), '| gelbe Markierungspixel in 01_Vergleich.jpg:', yellow(wd / 'Ordner' / '01_Vergleich.jpg'))
print('   Warnungen:', [w for w in plan['warnings'] if 'Blitz' in w or 'Reflex' in w])
r = subprocess.run([PY, str(res / 'graffiti.py'), '--input', str(inp), '--output', str(wd / 'CLI'), '--mode', 'klassisch', '--scale', '1'], capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
print('CLI graffiti.py: exit', r.returncode, '| gelbe Markierungspixel in 01_Vergleich.jpg:', yellow(wd / 'CLI' / '01_Vergleich.jpg'))
