"""Hinweis 2: Kosten der vollständigen Analyse je Vorschau (12 MP, ohne OCR) + Abbruchlatenz während OCR."""
from common import *
import time,json,subprocess,signal,os,sys
import analysis,graffiti,photo_prepare,flash
rng=np.random.default_rng(0)
# 12-MP-Testbild (4032x3024), strukturiert, als JPEG
yy,xx=np.mgrid[0:3024,0:4032].astype(np.float32)
a=np.stack([128+100*np.sin(xx/41.),128+90*np.cos(yy/29.),128+80*np.sin((xx+yy)/67.)],-1)+rng.normal(0,6,(3024,4032,1))
src=OUT/'e2_12mp.jpg';Image.fromarray(np.clip(a,0,255).astype(np.uint8)).save(src,quality=90)
def t(label,fn,*args,**kw):
    s=time.perf_counter();r=fn(*args,**kw);print(f'{label:32s} {time.perf_counter()-s:7.3f} s');return r
im=t('read_image (Dekodierung+RGB)',graffiti.read_image,src)
t('digest_image (SHA volle Pixel)',analysis.digest_image,im)
t('scan_features',analysis.scan_features,im)
t('flash.inspect',flash.inspect,im)
t('recipe (Papierkanten-Suche)',photo_prepare.recipe,im,src.name)
t('black_border (volle Auflösung)',analysis.black_border,im)
t('print_separators',analysis.print_separators,im)
t('analyze(ocr=False) gesamt',analysis.analyze,im,src,ocr=False)
# Ganze Vorschau wie die App: neuer Prozess je Reglerbewegung
req=OUT/'e2_req.json';req.write_text(json.dumps(dict(source=str(src),output=str(OUT/'e2_prev.png'),settings=dict(values=dict(contrast=20)))))
for i in range(2):
    s=time.perf_counter();r=subprocess.run([sys.executable,str(RES/'native_bridge.py'),'preview','--request',str(req)],capture_output=True,text=True)
    ev=[json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    print(f'native_bridge preview Lauf {i+1}: {time.perf_counter()-s:6.2f} s, letztes Ereignis={ev[-1]["type"]}')
s=time.perf_counter();subprocess.run([sys.executable,'-c',f'import sys;sys.path.insert(0,"{RES}");import native_bridge,graffiti'],check=True);print(f'nur Prozessstart+Importe: {time.perf_counter()-s:6.2f} s')
