# D12: Vorschaukosten (Analyse/Transform in voller Aufloesung) + D15 Decompression-Bomb
from common import *
import numpy as np,time,struct,zlib
from PIL import Image
from adjustments import Settings
from studio_backend import render_one
import graffiti
rng=np.random.default_rng(12)
Image.fromarray(rng.integers(0,255,(3024,4032,3),dtype=np.uint8)).save(OUT/'big12.jpg',quality=90)
for tag,kw in [('neutral',{}),('Ecken+Reflex+Retusche',dict(corners=[[.02,.02],[.98,.03],[.97,.98],[.03,.97]],glare_regions=[[.4,.4,.45,.45]],retouch_strokes=[dict(points=[[.2,.2],[.3,.3],[.4,.35]],radius=.02)],values={'glare':60}))]:
    t=time.time();r=render_one(OUT/'big12.jpg',OUT/'big12_prev.png',Settings(mode='klassisch',**kw),preview=True)
    print(f'12 MP {tag}: Vorschau {r["analysis"]["output_size"]} in {time.time()-t:.1f}s')
# D15: PNG-Kopf 20000x9000
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
p=OUT/'huge.png';p.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',20000,9000,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''))+chunk(b'IEND',b''))
try:graffiti.read_image(p)
except Exception as e:print('read_image 20000x9000:',type(e).__name__,e)
print('MAX_IMAGE_PIXELS',Image.MAX_IMAGE_PIXELS,'Fehlergrenze',2*Image.MAX_IMAGE_PIXELS)
