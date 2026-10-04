# D7: Belichtung/Schatten auf gamma-kodiertem Y bei konstanter Chroma
from common import *
import numpy as np,colorsys
from PIL import Image
from adjustments import render,CONTROL_SPEC
base={k:0 for k in CONTROL_SPEC}
def one(c,**kw):
    r=render(Image.new('RGB',(8,8),c),dict(base,**kw));return r.getpixel((4,4))
def hsv(c):h,s,v=colorsys.rgb_to_hsv(*[x/255 for x in c]);return (round(h*360),round(s,2),round(v*255))
for c,kw in [((100,20,20),{'exposure':100}),((250,220,30),{'exposure':-100}),((30,120,220),{'exposure':-100}),((60,25,10),{'shadows':70})]:
    o=one(c,**kw);print(c,kw,'->',o,'HSV',hsv(c),'->',hsv(o))
def lin(v):v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def enc(v):return 255*(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055)
for e,stops in ((50,1),(100,2)):
    g=one((118,118,118),exposure=e)[0];true=min(255,round(enc(min(1,lin(118)*2**stops))))
    first=next(x for x in range(256) if one((x,x,x),exposure=e)[0]==255)
    first_true=next(x for x in range(256) if lin(x)*2**stops>=1)
    print(f'Belichtung +{e} (Doku {stops} Blende): Grau 118 -> {g} (linear korrekt {true}); reines Weiss ab Eingang {first} (korrekt ab {first_true})')
