"""Hinweis 6: defekte/Grenz-Eingaben durch analyze -> json.dumps -> render_one (Vorschau und Export)."""
from common import *
import json,traceback,cv2,io
from pathlib import Path
import analysis,graffiti
from studio_backend import render_one
from adjustments import Settings
D=OUT/'e6';D.mkdir(exist_ok=True)
rng=np.random.default_rng(1)
def rgb(w,h):return Image.fromarray(rng.integers(0,255,(h,w,3),dtype=np.uint8))
cases={}
def add(name,fn):
    p=D/name;fn(p);cases[name]=p
add('1x1.png',lambda p:rgb(1,1).save(p))
add('1x5000.png',lambda p:rgb(1,5000).save(p))
add('5000x1.png',lambda p:rgb(5000,1).save(p))
add('2000x1.png',lambda p:rgb(2000,1).save(p))
add('49x49.png',lambda p:rgb(49,49).save(p))
add('schwarz.png',lambda p:Image.new('RGB',(800,600),0).save(p))
add('weiss.png',lambda p:Image.new('RGB',(800,600),(255,255,255)).save(p))
add('L.png',lambda p:rgb(400,300).convert('L').save(p))
add('P.png',lambda p:rgb(400,300).convert('P').save(p))
def rgba(p):
    a=np.array(rgb(400,300).convert('RGBA'));a[:,:200,3]=0;Image.fromarray(a).save(p)
add('RGBA_halbtransparent.png',rgba)
def i16(p):
    g=(np.tile(np.linspace(0,65535,400),(300,1))).astype(np.uint16);cv2.imwrite(str(p),g)
add('I16_grau_16bit.png',i16)
def rgb16(p):
    g=(np.tile(np.linspace(0,65535,400),(300,1))).astype(np.uint16);cv2.imwrite(str(p),np.dstack([g,g//2,65535-g]))
add('RGB_48bit.png',rgb16)
add('RGB_48bit.tif',lambda p:cv2.imwrite(str(p),np.dstack([(np.tile(np.linspace(0,65535,400),(300,1))).astype(np.uint16)]*3)))
add('CMYK.jpg',lambda p:rgb(400,300).convert('CMYK').save(p,quality=90))
def trunc(p):
    b=io.BytesIO();rgb(800,600).save(b,'JPEG',quality=90);p.write_bytes(b.getvalue()[:len(b.getvalue())//2])
add('abgeschnitten.jpg',trunc)
add('leer_0byte.jpg',lambda p:p.write_bytes(b''))
add('text_als.jpg',lambda p:p.write_text('Das ist kein Bild\n'))
def bomb(p):Image.new('L',(14000,13000),90).save(p)
add('gross_182MP.png',bomb)
for name,p in cases.items():
    line=f'{name:24s}'
    try:
        im=graffiti.read_image(p)
        try:
            pl=analysis.analyze(im,p,ocr=False);json.dumps(pl,allow_nan=False);line+=f' analyze OK ({im.size[0]}x{im.size[1]}, mean={np.array(im).mean():.0f})'
        except Exception as e:line+=f' analyze FEHLER {type(e).__name__}: {str(e)[:90]}'
    except Exception as e:line+=f' read_image FEHLER {type(e).__name__}: {str(e)[:110]}'
    for preview in (True,False):
        graffiti.SESSION.update(ocr_available=True,ai_available=True)
        try:
            r=render_one(p,D/f'{p.stem}_{"vorschau" if preview else "export"}.png',Settings(mode='klassisch'),preview)
            with Image.open(r['image']) as o:line+=f' | {"Vorschau" if preview else "Export"} OK {o.size} mean={np.array(o.convert("RGB")).mean():.0f}'
        except Exception as e:line+=f' | {"Vorschau" if preview else "Export"} FEHLER {type(e).__name__}: {str(e)[:100]}'
    print(line,flush=True)
