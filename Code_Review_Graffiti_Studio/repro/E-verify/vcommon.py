import sys
from pathlib import Path
V=Path(__file__).resolve().parent;RES=V/'Res';OUT=V/'out';OUT.mkdir(exist_ok=True)
sys.path.insert(0,str(RES))
import numpy as np
from PIL import Image,ImageDraw
def wall(size=(1800,1200),bg=(150,148,145),seed=7,margin=(0.09,0.11),outline=14):
    """Betonwand + gemaltes Piece mit dunkler Outline (kein Papier)."""
    rng=np.random.default_rng(seed);w,h=size
    a=np.empty((h,w,3),np.float32);a[:]=bg;a+=rng.normal(0,3,(h,w,1))
    x0,y0=int(w*margin[0]),int(h*margin[1]);x1,y1=w-x0,h-y0
    yy,xx=np.mgrid[y0:y1,x0:x1]
    a[y0:y1,x0:x1,0]=200-60*np.cos(xx/50.);a[y0:y1,x0:x1,1]=60+50*np.sin(yy/31.);a[y0:y1,x0:x1,2]=90+40*np.cos((xx-yy)/70.)
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8));d=ImageDraw.Draw(im)
    d.rectangle((x0,y0,x1,y1),outline=(15,15,15),width=outline)
    for i in range(5):d.polygon([(x0+80+i*300,y1-120),(x0+160+i*300,y0+120),(x0+260+i*300,y1-120)],fill=(240,240,40),outline=(0,0,0))
    return im
