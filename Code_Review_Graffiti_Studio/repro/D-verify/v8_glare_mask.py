# D8: Reflexbereich-Maske mit sigma=2 % der kurzen Bildseite
from common import *
import numpy as np,cv2,time
from PIL import Image
from photo_prepare import transform
W,H=4032,3024
for frac in (0.03,0.06,0.10):
    mask=np.zeros((H,W),np.float32);bw,bh=int(W*frac),int(H*frac);x0,y0=1800,1400
    mask[y0:y0+bh,x0:x0+bw]=1;s=max(4,min(H,W)*.02);m=cv2.GaussianBlur(mask,(0,0),s)
    print(f'Bereich {frac*100:.0f}% ({bw}x{bh}px) sigma={s:.1f}: Maske max {m.max():.2f}, Mittel innen {m[y0:y0+bh,x0:x0+bw].mean():.2f}, 60px ausserhalb {m[y0+bh//2,x0+bw+60]:.2f}')
# Wirkung end-to-end: Szene 63 + Schleier 52 im ganzen Bild
rng=np.random.default_rng(8)
a=np.clip(63+52+rng.normal(0,4,(H,W,3)),0,255).astype(np.uint8);im=Image.fromarray(a)
full=[[0,0],[1,0],[1,1],[0,1]];reg=[1800/W,1400/H,(1800+120)/W,(1400+90)/H]
t=time.time();o1=np.array(transform(im,dict(corners=full,glare_strength=.85)),np.float32);t1=time.time()-t
t=time.time();o2=np.array(transform(im,dict(corners=full,glare_strength=.85,glare_regions=[reg])),np.float32);t2=time.time()-t
i=(slice(1400,1490),slice(1800,1920))
print('Abdunklung im Rechteck: ohne Bereich %.1f, mit Bereich %.1f (%.0f %%); Laufzeit %.1fs / %.1fs'%(a[i].mean()-o1[i].mean(),a[i].mean()-o2[i].mean(),100*(a[i].mean()-o2[i].mean())/(a[i].mean()-o1[i].mean()),t1,t2))
print('Abdunklung 60..120px rechts ausserhalb: %.1f'%(a[1400:1490,1980:2040].mean()-o2[1400:1490,1980:2040].mean()))
