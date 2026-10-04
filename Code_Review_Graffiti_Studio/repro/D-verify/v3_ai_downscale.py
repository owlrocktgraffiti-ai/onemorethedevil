# D3: KI-Eingabe auf 3,5 MP verkleinert, Ergebnis beigemischt (Stub = LANCZOS x4, erfindet nichts)
from common import *
import numpy as np,cv2,os
from PIL import Image,ImageDraw
from adjustments import Settings
import graffiti
from studio_backend import render_one
W,H=4032,3024
a=np.full((H,W,3),180,np.uint8)
im=Image.fromarray(a);d=ImageDraw.Draw(im)
for y in range(100,H-100,40):
    for x in range(100,W-300,260):d.text((x,y),'ABC xyz 0815',fill=(20,20,20))
im.save(OUT/'text12mp.png')
def lapvar(p):
    g=cv2.cvtColor(np.array(Image.open(p).convert('RGB')),cv2.COLOR_RGB2GRAY);return cv2.Laplacian(g,cv2.CV_32F).var(),g
r1=render_one(OUT/'text12mp.png',OUT/'t_klass.png',Settings(mode='klassisch',scale=1,values={'sharpness':0,'clarity':0,'denoise':0,'vibrance':0,'shadows':0,'contrast':0}))
r2=render_one(OUT/'text12mp.png',OUT/'t_ki.png',Settings(mode='ki',scale=1,values={'sharpness':0,'clarity':0,'denoise':0,'vibrance':0,'shadows':0,'contrast':0}))
v1,g1=lapvar(r1['image']);v2,g2=lapvar(r2['image'])
print('klassisch Laplace-Var %.0f'%v1,r1['analysis']['effective_backend'])
print('ki        Laplace-Var %.0f'%v2,r2['analysis']['effective_backend'],'max|Diff| zu klassisch',int(np.abs(g1.astype(int)-g2).max()),'Hinweise',[n for n in r2['analysis']['executed'] if 'KI' in n or 'ESRGAN' in n])
