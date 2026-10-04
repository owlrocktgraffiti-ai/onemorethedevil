from vcommon import *
import json,hashlib,shutil,csv
import graffiti,analysis
from studio_backend import render_one,batch_files
from adjustments import Settings
# Zugfoto mit zentralem Blitzfleck
rng=np.random.default_rng(3);h,w=900,1400
a=np.zeros((h,w,3),np.float32);a[:]=(70,90,120);a+=rng.normal(0,6,(h,w,1))
yy,xx=np.mgrid[0:h,0:w];r=np.hypot(xx-700,yy-450);a+=np.clip(255*(1-r/90),0,255)[...,None]*1.2
im=Image.fromarray(np.clip(a,0,255).astype(np.uint8));src=OUT/'v_blitz.jpg';im.save(src,quality=95)
fp=analysis.digest_image(graffiti.read_image(src))
base=analysis.analyze(graffiti.read_image(src),src,ocr=False)
print('OHNE Referenz warnings:',base['warnings'])
# Referenzeintrag in der KOPIE
(RES/'Referenzkorrekturen').mkdir(exist_ok=True);ref=RES/'Referenzkorrekturen/v_ref.png'
Image.new('RGB',(1400,900),(70,90,120)).save(ref)
rec=[dict(source_name='v_blitz.jpg',image_sha256=fp,cached='Referenzkorrekturen/v_ref.png',cached_sha256=hashlib.sha256(ref.read_bytes()).hexdigest(),description='Test',generative_reconstruction=True)]
orig=(RES/'Bekannte_Retuschen.json').read_text()
(RES/'Bekannte_Retuschen.json').write_text(json.dumps(rec))
try:
    graffiti.SESSION.update(ocr_available=False,ai_available=False)
    r=render_one(src,OUT/'v_e3_prev.png',Settings(),True);p=r['analysis']
    print('E3 Vorschau: warnings',p['warnings'],'| effective_backend',p['effective_backend'],'| executed0',p['executed'][0])
    with Image.open(r['image']) as o:print('E3 PNG info:',o.info, '| text' ,getattr(o,'text',None))
    out=OUT/'v_e3_batch';shutil.rmtree(out,ignore_errors=True);shutil.rmtree(OUT/'v_e3_batch.zip',ignore_errors=True)
    s=Settings(export='instagram');res=batch_files([src],out,s)
    print('E3 Ordner-Ergebnis warnings:',res['warnings'])
    print('E3 CSV:',list(csv.reader(open(out/'Protokoll.csv',encoding='utf-8-sig')))[1][2:])
    print('E3 Dateien:',sorted(x.name for x in out.rglob('*') if x.is_file()))
    # E4
    pl,_=Settings(use_saved_retouches=False).prepare_plan(analysis.analyze(graffiti.read_image(src),src,ocr=False))
    print('E4 use_saved_retouches=False: cached im Plan',('cached_correction' in pl),'| warnings',pl['warnings'])
    pl,_=Settings(rotation=0).prepare_plan(analysis.analyze(graffiti.read_image(src),src,ocr=False))
    print('E4 rotation=0: cached im Plan',('cached_correction' in pl),'| warnings',pl['warnings'])
finally:
    (RES/'Bekannte_Retuschen.json').write_text(orig)
# E4 Teil 2: Papierkandidat + geometry aus
wim=wall(margin=(0.05,0.06),outline=20);wp=OUT/'v_e4_wand.png';wim.save(wp)
pl0=analysis.analyze(wim,wp,ocr=True)  # Engine fehlt -> Warnung
pl,_=Settings(geometry='aus').prepare_plan(pl0)
print('E4 geometry=aus: preparation',pl.get('preparation'),'| warnings',pl['warnings'],'| actions',[x for x in pl['actions'] if 'Papier' in x])
