"""Freigegebene Bilder: Regler werden still ignoriert; Instagram/Vergleich nutzen EXIF-unkorrigierte Pixel."""
from common import *
import json,shutil,subprocess,sys,hashlib
from pathlib import Path
import analysis,graffiti
R9=E/'Resources_e9';shutil.rmtree(R9,ignore_errors=True);shutil.copytree(RES,R9,ignore=shutil.ignore_patterns('__pycache__'))
# 600x400 gespeichert, EXIF-Orientierung 6 => Anzeige hochkant 400x600 (typisches iPhone-JPEG)
a=np.zeros((400,600,3),np.uint8);a[:,:300]=(220,40,40);a[:,300:]=(40,40,220);a[:40,:]=(255,255,0)
im=Image.fromarray(a);ex=im.getexif();ex[0x0112]=6;src=OUT/'e9_freigegeben.jpg';im.save(src,quality=95,exif=ex.tobytes())
shown=graffiti.read_image(src);print('Anzeigegröße nach EXIF:',shown.size)
fp=analysis.digest_image(shown);(R9/'Freigegebene_Bilder.json').write_text(json.dumps([dict(image_sha256=fp,description='Test')]))
def bridge(cmd,req):
    q=OUT/f'e9_{cmd}_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(R9/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
res=bridge('preview',dict(source=str(src),output=str(OUT/'e9_prev.png'),settings=dict(values=dict(contrast=80,exposure=50,saturation=-100))))['result']
print('Vorschau mit Kontrast +80, Belichtung +50, Sättigung -100: Datei =',Path(res['image']).name,'| byte-identisch mit Original:',hashlib.sha256(open(res['image'],'rb').read()).hexdigest()==hashlib.sha256(src.read_bytes()).hexdigest(),'| warnings =',res['analysis']['warnings'],'| controls im Plan:',res['analysis']['controls']['contrast'])
out=OUT/'e9_batch';shutil.rmtree(out,ignore_errors=True);Path(str(out)+'.zip').unlink(missing_ok=True)
res=bridge('batch',dict(files=[str(src)],output=str(out),settings=dict(export='instagram')))['result']
base=Image.open(out/'Instagram'/'01_e9_freigegeben'/'Panorama_Gemeinsame_Basis.png');arr=np.array(base)
nz=np.argwhere(arr.sum(axis=2)>0);y0,x0=nz.min(0);y1,x1=nz.max(0)
print('Instagram-Basis: Bildinhalt',x1-x0+1,'x',y1-y0+1,'(Anzeige wäre hochkant 400x600 -> Inhalt müsste höher als breit sein)')
cmp=np.array(Image.open(out/'01_Vergleich.jpg'))
print('Vergleichsbild linke Hälfte (Original, mit EXIF) Höhe/Breite des Inhalts vs. rechte Hälfte (Ergebnis):')
for name,part in (('links',cmp[20:,0:380]),('rechts',cmp[20:,390:770])):
    m=np.argwhere(np.abs(part.astype(int)-238).sum(axis=2)>30);print('  ',name,'Breite',np.ptp(m[:,1])+1,'Höhe',np.ptp(m[:,0])+1)
