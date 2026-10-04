"""G13: defektes Modell (Stub, Exit 1) - wie oft wird es bei App-Standardeinstellungen aufgerufen?"""
import json
from PIL import Image
from vcommon import *
res = fresh_resources('g13'); inp = res.parent / 'in'; inp.mkdir()
for i in range(3): Image.new('RGB', (900, 600), (90 + 20*i, 100, 120)).save(inp / f'f{i}.png')
calls = res.parent / 'calls.txt'
stub = res / 'engine/realesrgan-ncnn-vulkan'
stub.write_text(f'#!{PY}\nimport sys\nopen({str(calls)!r},"a").write("x\\n")\nprint("vkCreateInstance failed");sys.exit(1)\n'); stub.chmod(0o755)
default = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])
n = lambda: len(calls.read_text().splitlines()) if calls.exists() else 0
for k in (1, 2):
    code, ev, err = bridge(res, 'preview', dict(source=str(inp / 'f0.png'), output=str(res.parent / f'p{k}.png'), settings=dict(default, values={'contrast': 10*k})))
    print(f'Vorschau {k}: Modellaufrufe bisher={n()} | Warnung: {[w for w in ev[-1]["result"]["analysis"]["warnings"] if "KI" in w]}')
before = n()
code, ev, err = bridge(res, 'batch', dict(files=[str(p) for p in sorted(inp.glob('*.png'))], output=str(res.parent / 'batch'), settings=default))
print(f'Stapel mit 3 Fotos: Modellaufrufe im Stapel={n() - before}')
