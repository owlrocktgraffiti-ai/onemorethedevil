"""F10: Dauer des PNG-Speicherns (graffiti.py:125, Pillow-Standard zlib-Stufe 6) vs. compress_level=1 fuer die
60-MP-Ausgabe aus f2 – Phase ohne Checkpoint/Abbruch. Aufruf: venv/bin/python repro/F/f10_png_level.py"""
import time
from pathlib import Path
from PIL import Image
p = next(Path(__file__).parent.glob('work/f2/Ausgabe/Foto_ohne_Abbruch/gross.png'))
im = Image.open(p); im.load(); print('Bild', im.size, round(im.width * im.height / 1e6, 1), 'MP')
for kw in ({}, {'compress_level': 1}):
    t = time.monotonic(); out = p.with_name('probe.png'); im.save(out, format='PNG', **kw)
    print(kw or 'Standard (Stufe 6)', f'{time.monotonic() - t:.1f}s', round(out.stat().st_size / 2**20, 1), 'MiB')
    out.unlink()
