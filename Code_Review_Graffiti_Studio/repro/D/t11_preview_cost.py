"""Zusatz: Kosten einer Vorschau (1440x1000) – Analyse, Entzerrung, Reflex und Retusche laufen in voller Auflösung vor dem Verkleinern."""
import time,numpy as np,struct,zlib,io
from PIL import Image
import common
from adjustments import Settings
import graffiti
OUT=common.OUT/'t11';OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(11)
for W,H in ((4032,3024),(8064,6048)):
    src=OUT/f'img_{W}.jpg'
    if not src.exists():Image.fromarray((rng.normal(0,30,(H//4,W//4,3))+120).clip(0,255).astype(np.uint8)).resize((W,H)).save(src,quality=90)
    corners=[[.05,.04],[.95,.06],[.93,.95],[.06,.97]]
    strokes=[dict(points=[[.2+.01*i,.3] for i in range(30)],radius=.05),dict(points=[[.6,.6]],radius=.05)]
    for name,s in [('neutral',Settings(mode='klassisch')),('Ecken+Reflex+Retusche',Settings(mode='klassisch',corners=corners,glare_regions=[[.4,.4,.7,.7]],retouch_strokes=strokes,values={'glare':60}))]:
        t=time.time();im,plan=graffiti.process(src,OUT/'p.png','klassisch',0,'auto','auto',None,s,(1440,1000));dt=time.time()-t
        print(f'{W}x{H} {name:24s}: Vorschau {im.size} in {dt:.1f}s')
# Pixelgrenze von Pillow (Decompression-Bomb-Schutz) für große Panoramen
def png_header_only(w,h):
    raw=io.BytesIO();Image.new('RGB',(1,1)).save(raw,'PNG');b=bytearray(raw.getvalue())
    ihdr=struct.pack('>IIBBBBB',w,h,8,2,0,0,0);b[16:29]=ihdr;b[29:33]=struct.pack('>I',zlib.crc32(b'IHDR'+ihdr));return bytes(b)
p=OUT/'pano_180MP.png';p.write_bytes(png_header_only(20000,9000))
try:graffiti.read_image(p)
except Exception as e:print('read_image 20000x9000:',type(e).__name__,str(e)[:140])
