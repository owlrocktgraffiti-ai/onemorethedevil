# D14: unplausible KI-Ausgabe (Exit 0) wird beigemischt
from common import *
import numpy as np,os
from PIL import Image
from adjustments import Settings
from studio_backend import render_one
import graffiti
Image.fromarray(np.clip(np.random.default_rng(14).normal(125,20,(400,500,3)),0,255).astype(np.uint8)).save(OUT/'ai_in.png')
for mode in ('lanczos','black','tiny'):
    os.environ['STUB_MODE']=mode;graffiti.SESSION['ai_available']=True
    r=render_one(OUT/'ai_in.png',OUT/f'ai_{mode}.png',Settings(mode='ki',scale=2))
    o=np.array(Image.open(r['image']));print(f'{mode:8s} backend={r["analysis"]["effective_backend"]} Ergebnis-Mittel={o.mean():.1f} Warnungen={[w for w in r["analysis"]["warnings"] if "KI" in w]}')
