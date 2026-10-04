"""G7: Empfindlichkeit von paper_confidence gegenueber der genauen Lage des Wagenkastens (warmer Hintergrund)."""
import sys
from vcommon import *
sys.path.insert(0, str(fresh_resources('g7s3')))
import numpy as np
from PIL import Image, ImageDraw
from photo_prepare import recipe
from analysis import paper_confidence
rng = np.random.default_rng(11)
hits = 0; total = 0
for x0 in (40, 60, 75, 90):
    for y0, y1 in ((100, 800), (120, 820), (130, 800), (150, 850)):
        a = np.clip(np.full((1000, 1500, 3), (175, 105, 65), int) + rng.integers(-10, 11, (1000, 1500, 1)), 0, 255).astype(np.uint8)
        im = Image.fromarray(a); d = ImageDraw.Draw(im)
        d.rectangle((x0, y0, 1500 - x0, y1), fill=(195, 198, 205))
        for i in range(6):
            cx = x0 + 60 + i*210; d.ellipse((cx, y0+80, cx+170, y1-90), fill=[(230, 40, 40), (250, 200, 30), (40, 160, 230)][i % 3])
        cfg, reason = recipe(im, 'x.png'); conf = paper_confidence(im, cfg) if reason.startswith('Papierkanten') else None
        total += 1; hits += bool(conf and conf >= .86)
        print(f'Wagen x {x0}..{1500-x0} y {y0}..{y1}: conf={conf} {"ZUSCHNITT" if conf and conf >= .86 else ""}')
print(f'automatisch zugeschnitten: {hits}/{total}')
