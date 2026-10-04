"""Zusatz: Welche Schritte kosten in transform() bei 48 MP? (gleiche Eingabe wie t11)"""
import time,numpy as np,cv2
from PIL import Image
import common
from photo_prepare import transform
from graffiti import read_image
img=read_image(common.OUT/'t11'/'img_8064.jpg')
corners=[[.05,.04],[.95,.06],[.93,.95],[.06,.97]]
strokes=[dict(points=[[.2+.01*i,.3] for i in range(30)],radius=.05),dict(points=[[.6,.6]],radius=.05)]
for name,cfg in [('nur Entzerrung',dict(corners=corners,rotate=0,glare_strength=0)),
                 ('+ Reflex global',dict(corners=corners,rotate=0,glare_strength=.51)),
                 ('+ Reflex mit Bereich',dict(corners=corners,rotate=0,glare_strength=.51,glare_regions=[[.4,.4,.7,.7]])),
                 ('+ Retusche',dict(corners=corners,rotate=0,glare_strength=0,retouch_strokes=strokes,retouch_strength=1))]:
    t=time.time();transform(img,cfg);print(f'{name:22s}: {time.time()-t:.1f}s')
H,W=6000,7500;m=np.zeros((H,W),np.float32);m[2000:4000,3000:5000]=1
t=time.time();cv2.GaussianBlur(m,(0,0),max(4,min(H,W)*.02));print(f'GaussianBlur Maske 45 MP, sigma {min(H,W)*.02:.0f}: {time.time()-t:.1f}s')
