# D4: feste Pixelradien nach Skalierung -> Vorschau vs. Export
from common import *
import numpy as np,cv2
from PIL import Image,ImageDraw
from adjustments import render,CONTROL_SPEC
rng=np.random.default_rng(3)
W,H=4032,3024
a=np.full((H,W),150,np.float32)
im=Image.fromarray(a.astype(np.uint8));d=ImageDraw.Draw(im)
for y in range(50,H-50,60):
    for x in range(50,W-300,300):d.text((x,y),'Graffiti 123',fill=40)
a=np.array(im,np.float32)+rng.normal(0,9,(H,W));src=Image.fromarray(np.clip(a,0,255).astype(np.uint8)).convert('RGB')
f=min(1440/W,1000/H);pw,ph=round(W*f),round(H*f)
base={k:0 for k in CONTROL_SPEC}
def hf(img):g=np.array(img.convert('L'),np.float32);return float(np.mean(np.abs(g-cv2.GaussianBlur(g,(0,0),1.0))))
prev_in=src.resize((pw,ph),Image.Resampling.LANCZOS)
exp1_in=src;exp2_in=src.resize((W*2,H*2),Image.Resampling.LANCZOS)
def down(img):return img.resize((pw,ph),Image.Resampling.LANCZOS)
n_p=hf(render(prev_in,base));n_1=hf(down(render(exp1_in,base)));n_2=hf(down(render(exp2_in,base)))
for k in ['denoise','sharpness','compression']:
    v=dict(base,**{k:100})
    p=hf(render(prev_in,v));e1=hf(down(render(exp1_in,v)));e2=hf(down(render(exp2_in,v)))
    print(f'{k:11s} Vorschau HF {n_p:.2f}->{p:.2f} ({(p/n_p-1)*100:+.0f}%) | Export1x↓ {n_1:.2f}->{e1:.2f} ({(e1/n_1-1)*100:+.0f}%) | Export2x↓ {n_2:.2f}->{e2:.2f} ({(e2/n_2-1)*100:+.0f}%)')
