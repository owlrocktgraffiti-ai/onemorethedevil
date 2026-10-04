# D6: Farbstich-Erkennung / Weissabgleich-Regler
from common import *
import numpy as np
from PIL import Image
from analysis import scan_features
from adjustments import Settings
rng=np.random.default_rng(6)
print('Theoretische Grenze: OpenCV S<=39 -> max/min <= %.4f, Schwelle 1.18'%(1/(1-39.5/255)))
for noise in (2,6):
    row=[]
    for c in (0.04,0.06,0.08,0.09,0.10,0.15,0.25):
        base=np.array([140*(1+c),140,140*(1-c)])
        a=np.clip(base+rng.normal(0,noise,(400,600,3)),0,255).astype(np.uint8)
        f=scan_features(Image.fromarray(a))
        row.append(f'R/B={(1+c)/(1-c):.2f}:{"JA" if f["cast_suspected"] else "nein"}')
    print('Rauschen',noise,' | '.join(row))
# Szene: 50 % graue Wand mit Stich + 50 % bunte Farbe
a=np.zeros((400,600,3));a[:,:300]=(160,140,115);a[:,300:]=(200,40,60)
a=np.clip(a+rng.normal(0,3,a.shape),0,255).astype(np.uint8)
f=scan_features(Image.fromarray(a));print('Gelbstich (160,140,115): cast',f['cast_suspected'],'gains',f['white_balance_rgb'])
plan=dict(look='kraeftig',features=f,warnings=[],actions=[],white_balance_rgb=f['white_balance_rgb'],preparation=None)
p,c=Settings(values={'white_balance':100}).prepare_plan(plan);print('Regler 100 -> white_balance_rgb',p['white_balance_rgb'])
