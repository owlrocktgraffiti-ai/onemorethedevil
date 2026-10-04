"""Hinweis 5: panel_candidates/review_regions in der nativen App ohne Wirkung/Anzeige."""
from common import *
import json,shutil,subprocess,sys
from pathlib import Path
# Langer Scan mit drei Abzügen, getrennt durch weiße Stege (Seitenverhältnis 3,3)
rng=np.random.default_rng(2);h,w=600,2000
a=rng.uniform(30,220,(h,w,3)).astype(np.uint8)
for x in (650,1330):a[:,x:x+20]=255
# heller Blitzfleck in Feld 2 (für review_regions)
yy,xx=np.mgrid[0:h,0:w];r=np.hypot(xx-1000,yy-300);a[r<45]=255
src=OUT/'e5_scan.png';Image.fromarray(a).save(src)
import analysis,graffiti
pl=analysis.analyze(graffiti.read_image(src),src,ocr=False)
print('Analyse: panel_candidates=',pl.get('panel_candidates'),'| review_regions=',pl.get('review_regions'))
print('warnings=',pl['warnings'])
def bridge(cmd,req):
    q=OUT/f'e5_{cmd}_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(RES/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
out=OUT/'e5_batch';shutil.rmtree(out,ignore_errors=True);Path(str(out)+'.zip').unlink(missing_ok=True)
res=bridge('batch',dict(files=[str(src)],output=str(out),settings=dict(mode='klassisch')))['result']
print('Native Ordner-Export, Dateien:',sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file()))
cmp=np.array(Image.open(out/'01_Vergleich.jpg').convert('RGB')).astype(int)
yellow=((abs(cmp[...,0]-255)<40)&(abs(cmp[...,1]-206)<40)&(cmp[...,2]<110)).sum()
print('Gelbe Markierungspixel (#ffce33) im nativen Vergleichsbild:',int(yellow))
out3=OUT/'e5_single';shutil.rmtree(out3,ignore_errors=True);Path(str(out3)+'.zip').unlink(missing_ok=True)
res=bridge('export',dict(source=str(src),output=str(out3/'e5_scan.png'),settings=dict(mode='klassisch')))['result']
print('Native Einzel-Export, Dateien:',sorted(str(p.relative_to(out3)) for p in out3.rglob('*') if p.is_file()),'| UI-Warnungen:',res['warnings'])
