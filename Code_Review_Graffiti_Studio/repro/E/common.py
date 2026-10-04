"""Gemeinsame Helfer für Bereich E. Importiert die KOPIE unter repro/E/Resources."""
import sys,os
from pathlib import Path
E=Path(__file__).resolve().parent
RES=E/'Resources'
OUT=E/'out';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(RES))
import numpy as np
from PIL import Image,ImageDraw

def wall_with_panel(size=(1600,1200),bg=(128,128,128),noise=4,inset=(0.10,0.08),seed=1,panel_texture=True,frame=True,solid=None,letter=(250,250,250)):
    """Gleichmäßiger Hintergrund (Wand/Himmel) + großes, farbiges Graffiti-Panel (kein Papierabzug)."""
    rng=np.random.default_rng(seed);w,h=size
    a=np.empty((h,w,3),np.float32);a[:]=bg;a+=rng.normal(0,noise,(h,w,1))
    x0,y0=int(w*inset[0]),int(h*inset[1]);x1,y1=w-x0,h-y0
    if solid is not None:
        a[y0:y1,x0:x1]=solid
    elif panel_texture:
        yy,xx=np.mgrid[y0:y1,x0:x1]
        a[y0:y1,x0:x1,0]=120+100*np.sin(xx/37.)
        a[y0:y1,x0:x1,1]=90+80*np.cos(yy/23.)
        a[y0:y1,x0:x1,2]=160+60*np.sin((xx+yy)/51.)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    d=ImageDraw.Draw(im)
    if frame:d.rectangle((x0,y0,x1,y1),outline=(20,20,20),width=10)  # gemalte Outline/Rahmen um das Wandbild
    for i in range(6):
        d.rectangle((x0+60+i*190,y0+150,x0+200+i*190,y0+600),fill=letter,outline=(0,0,0),width=12)
    return im,(x0,y0,x1,y1)
