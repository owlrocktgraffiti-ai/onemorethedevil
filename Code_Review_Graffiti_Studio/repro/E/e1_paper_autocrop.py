"""Hinweis 1: unbekanntes Wand-/Zugfoto wird automatisch als Papierabzug zugeschnitten und entzerrt."""
from common import *
import json
from pathlib import Path
import analysis,graffiti
from studio_backend import render_one,batch_files
from adjustments import Settings
assert not (RES/'engine/orientation').exists()
cases={}
im,box=wall_with_panel();p=OUT/'e1_wand_grau.jpg';im.save(p,quality=92);cases['grau']=p
im2,_=wall_with_panel(bg=(14,12,10),noise=3,seed=2);p2=OUT/'e1_nacht_dunkel.jpg';im2.save(p2,quality=92);cases['nacht']=p2
# warmer Backstein/Natriumlicht-Hintergrund, NICHT gleichmäßig
rng=np.random.default_rng(3);bg=np.zeros((1200,1600,3),np.float32);base=rng.uniform(60,200,(1200,1600,1))
bg[:,:,0]=base[:,:,0];bg[:,:,1]=base[:,:,0]/1.25;bg[:,:,2]=base[:,:,0]/1.6
im4,_=wall_with_panel(frame=False,solid=(230,200,40),bg=(70,70,75),seed=5);p4=OUT/'e1_gelbe_flaeche.jpg';im4.save(p4,quality=92);cases['gelb']=p4
im3,_=wall_with_panel(seed=4);a3=np.array(im3).astype(np.float32);x0,y0,x1,y1=box;mask=np.ones((1200,1600),bool);mask[y0:y1,x0:x1]=False
a3[mask]=bg[mask];im3=Image.fromarray(np.clip(a3,0,255).astype(np.uint8));p3=OUT/'e1_backstein_warm.jpg';im3.save(p3,quality=92);cases['warm']=p3
for name,path in cases.items():
    src=graffiti.read_image(path)
    for ocr in (False,True):
        plan=analysis.analyze(src,path,ocr=ocr)
        print(f'[{name}] ocr={ocr} paper_confidence={plan.get("paper_confidence")} preparation={bool(plan.get("preparation"))} glare={ (plan.get("preparation") or {}).get("glare_strength")} warnings={plan["warnings"]}')
    graffiti.SESSION.update(ocr_available=True,ai_available=True)
    r=render_one(path,OUT/f'e1_{name}_export.png',Settings(mode='klassisch',scale=1),False)
    with Image.open(r['image']) as out:print(f'[{name}] Export render_one: Original {src.size} -> Ausgabe {out.size}; executed={r["analysis"]["executed"][:2]}; warnings={r["analysis"]["warnings"]}')
# Stapel: erstes Foto deaktiviert OCR (Laufzeit fehlt) -> zweites Foto wird OHNE jede Warnung zugeschnitten
graffiti.SESSION.update(ocr_available=True,ai_available=True)
plain=Image.fromarray((np.random.default_rng(9).uniform(0,255,(900,1200,3))).astype(np.uint8));pp=OUT/'e1_a_normal.jpg';plain.save(pp)
import shutil
outdir=OUT/'e1_batch'
shutil.rmtree(outdir,ignore_errors=True);Path(str(outdir)+'.zip').unlink(missing_ok=True)
im5,_=wall_with_panel(letter=(230,60,40),seed=7);p5=OUT/'e1_wand_ohne_weiss.jpg';im5.save(p5,quality=92)
res=batch_files([pp,cases['grau'],p5],outdir,Settings(mode='klassisch',scale=1))
print('Stapel:',json.dumps(res,ensure_ascii=False))
print(open(outdir/'Protokoll.csv',encoding='utf-8-sig').read())
for f in sorted(outdir.glob('*.json')):
    pl=json.loads(f.read_text())
    if 'output_size' in pl:print(f.name,'preparation=',bool(pl.get('preparation')),'output_size=',pl['output_size'],'warnings=',pl['warnings'])
