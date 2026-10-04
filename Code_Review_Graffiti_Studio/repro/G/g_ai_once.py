"""Chat_Korrekturen.md Z.27: 'Lokale KI funktioniert nicht / kein Metal | Einmaliger Versuch, danach in diesem Lauf
klassische Bildverarbeitung'. Die native App startet pro Vorschau einen NEUEN Python-Prozess (GraffitiStudio.swift:91-97),
SESSION (graffiti.py:12) ist prozesslokal. Stub-Modell in der KOPIE: zaehlt Aufrufe, wartet 2 s, scheitert."""
import sys, time, json
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
from PIL import Image
res = fresh_resources('ai_once'); wd = res.parent
counter = wd / 'aufrufe.txt'
stub = res / 'engine' / 'realesrgan-ncnn-vulkan'
stub.write_text(f'#!/bin/sh\necho x >> {counter}\nsleep 2\necho "vkCreateInstance failed: kein Metal" >&2\nexit 1\n'); stub.chmod(0o755)
for i in range(3): Image.new('RGB', (800, 600), (40 + 50 * i, 100, 150)).save(wd / f'foto{i}.jpg')
def calls(): return len(counter.read_text().splitlines()) if counter.exists() else 0
setting = dict(mode='ki', scale=2)
for n in range(2):
    t = time.monotonic()
    code, ev, err = bridge(res, 'preview', dict(source=str(wd / 'foto0.jpg'), output=str(wd / f'p{n}.png'), settings=setting), wd)
    plan = ev[-1]['result']['analysis']
    print(f'Vorschau {n+1}: {time.monotonic()-t:.1f}s, Modellaufrufe bisher={calls()}, backend={plan["effective_backend"]}, Warnung KI:',
          [w for w in plan['warnings'] if 'KI' in w])
before = calls(); t = time.monotonic()
code, ev, err = bridge(res, 'batch', dict(files=[str(wd / f'foto{i}.jpg') for i in range(3)], output=str(wd / 'Ordner'), settings=setting), wd)
print(f'Stapel mit 3 Fotos: {time.monotonic()-t:.1f}s, Modellaufrufe im Stapel={calls()-before}, Ergebnis={ev[-1]["type"]}')
