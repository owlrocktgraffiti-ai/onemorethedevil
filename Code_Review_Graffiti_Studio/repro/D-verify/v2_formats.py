# D2: Eingabemodi in read_image
from common import *
import numpy as np
from PIL import Image
import graffiti
from adjustments import Settings
from studio_backend import render_one
ramp=np.tile(np.linspace(0,1,256,dtype=np.float64),(64,1))
cases={}
cases['I16.png']=Image.fromarray((ramp*65535).astype(np.uint16))
cases['I16.tif']=Image.fromarray((ramp*65535).astype(np.uint16))
cases['F.tif']=Image.fromarray(ramp.astype(np.float32))
rgba=np.zeros((64,256,4),np.uint8);rgba[...,:3]=(ramp*255).astype(np.uint8)[...,None];rgba[...,3]=255;rgba[:32,:,3]=0
cases['RGBA.png']=Image.fromarray(rgba)
cases['CMYK.jpg']=Image.new('CMYK',(256,64),(0,199,199,31))
for name,im in cases.items():
    p=OUT/('fmt_'+name);im.save(p)
    with Image.open(p) as o:mode=o.mode
    r=np.array(graffiti.read_image(p))
    print(f'{name:9s} Modus={mode:6s} Spalten64/128/192 (Zeile 40)={r[40,64,0]}/{r[40,128,0]}/{r[40,192,0]} transparente Zeile0 Spalte200={r[0,200]}')
# Pipeline 16 Bit
big=np.tile(np.linspace(0,65535,1200),(900,1)).astype(np.uint16);big[300:600,200:1000]=20000
Image.fromarray(big).save(OUT/'scan16.png')
res=render_one(OUT/'scan16.png',OUT/'scan16_out.png',Settings(mode='klassisch'))
o=np.array(Image.open(res['image']));print('scan16 Ergebnis',o.shape,'Mittel %.1f Std %.1f'%(o.mean(),o.std()),'Warnungen',res['analysis']['warnings'],'Backend',res['analysis']['effective_backend'])
