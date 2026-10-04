import sys,os
from pathlib import Path
V=Path(__file__).resolve().parent;sys.path.insert(0,str(V/'Res_ocr'))
import numpy as np
from PIL import Image
sys.path.insert(1,str(V));from vcommon import wall,OUT,RES;sys.path.remove(str(RES));sys.path.insert(0,str(V/"Res_ocr"))
from studio_backend import render_one
from adjustments import Settings
import graffiti
graffiti.SESSION['ai_available']=False
# E12: Querformat-Zugfoto ohne Rezept, OCR "sicher 90"
os.environ['VSTUB_ROT']='90'
z=Image.fromarray(np.random.default_rng(5).integers(40,200,(900,1200,3)).astype(np.uint8));zp=OUT/'v_zug.png';z.save(zp)
r=render_one(zp,OUT/'v_e12.png',Settings(),True)['analysis']
print('E12 Zug',z.size,'->',r['output_size'],'rotation',r.get('rotation'),'warnings',r['warnings'],'actions mit Drehung',[x for x in r['actions'] if 'Dreh' in x])
# E13 OCR-Teil: Editor (Vollbild-Ecken, rotation aus preparation=None -> nil) + Region
r2=render_one(zp,OUT/'v_e13o.png',Settings(corners=[[0,0],[1,0],[1,1],[0,1]],glare_regions=[[.4,.4,.5,.5]]),True)['analysis']
print('E13 OCR nach Editor',r2['output_size'],'rotation',r2.get('rotation'),'prep rotate',r2['preparation']['rotate'])
# E1 mit OCR sicher 0
os.environ['VSTUB_ROT']='0'
w=wall(margin=(0.05,0.06),outline=20);wp=OUT/'v_e1_ocr.png';w.save(wp)
r3=render_one(wp,OUT/'v_e1o.png',Settings(),True)['analysis']
print('E1 OCR sicher 0°: Wand',w.size,'->',r3['output_size'],'warnings',r3['warnings'],'exec0',r3['executed'][0])
