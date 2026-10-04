from vcommon import *
import time,graffiti,analysis
from studio_backend import render_one
from adjustments import Settings
from photo_prepare import transform
graffiti.SESSION.update(ocr_available=False,ai_available=False)
a=np.random.default_rng(0).integers(0,255,(4032,3024,3),dtype=np.uint8);p=OUT/'v_12mp.jpg';Image.fromarray(a).save(p,quality=90)
t=time.perf_counter();im=graffiti.read_image(p);t1=time.perf_counter();analysis.analyze(im,p,ocr=False);t2=time.perf_counter()
print(f'read_image {t1-t:.2f}s analyze {t2-t1:.2f}s')
for v in (10,20):
    t=time.perf_counter();render_one(p,OUT/'v_e9.png',Settings(values=dict(contrast=v)),True);print(f'Vorschau contrast={v}: {time.perf_counter()-t:.2f}s')
t=time.perf_counter();transform(im,dict(corners=[[0.012,0.034],[0.847,0.039],[0.856,0.927],[0.087,0.943]],rotate=90,glare_strength=.595));print(f'transform voll {time.perf_counter()-t:.2f}s')
