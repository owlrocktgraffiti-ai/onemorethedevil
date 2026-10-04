"""K1: Ein einziger OCR-Ausfall im Ordnerexport schaltet die OCR für alle folgenden Fotos ab:
Abzüge werden ohne Drehung und ohne Warnung exportiert (Vorschau dreht sie)."""
import json,subprocess,sys,os,shutil
from pathlib import Path
import numpy as np
from PIL import Image
K=Path(__file__).resolve().parent;R=K/'Resources';OUT=K/'out'
rng=np.random.default_rng(3)
Image.fromarray((rng.random((900,1200,3))*255).astype(np.uint8)).save(OUT/'c_wand.jpg')
def bridge(cmd,req,fail_first):
    q=OUT/f'k1_{cmd}_req.json';q.write_text(json.dumps(req));ctr=OUT/'k1_counter';ctr.write_text('0')
    p=subprocess.run([sys.executable,str(R/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True,env=dict(os.environ,OCR_COUNTER=str(ctr),OCR_FAIL_FIRST=fail_first))
    ev=[json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    return ev[-1]
# Vorschau einzeln (OCR funktioniert)
for name in ('b_abzug.jpg','c_wand.jpg'):
    r=bridge('preview',dict(source=str(OUT/name),output=str(OUT/f'k1_prev_{name}.png'),settings=dict(mode='klassisch')),'0')['result']
    with Image.open(r['image']) as im:size=im.size
    a=r['analysis'];print('VORSCHAU',name,size,'prep.rotate=',(a.get('preparation') or {}).get('rotate'),'rotation=',a.get('rotation'),'warnings=',a['warnings'])
# Ordnerexport: erster OCR-Aufruf scheitert
out=OUT/'k1_batch'
if out.exists():shutil.rmtree(out)
if out.with_suffix('.zip').exists():out.with_suffix('.zip').unlink()
r=bridge('batch',dict(files=[str(OUT/'a_abzug.jpg'),str(OUT/'b_abzug.jpg'),str(OUT/'c_wand.jpg')],output=str(out),settings=dict(mode='klassisch')),'1')
print('BATCH-Ergebnis',r['type'],r.get('result',{}).get('warnings'))
for line in (out/'Protokoll.csv').read_text(encoding='utf-8-sig').splitlines():print('  CSV',line)
for j in sorted(out.glob('0*.json')):
    a=json.loads(j.read_text());img=Path(a['output_path'])
    with Image.open(img) as im:size=im.size
    print('  BATCH',img.name,size,'prep.rotate=',(a.get('preparation') or {}).get('rotate'),'rotation=',a.get('rotation'),'orientation=',a.get('orientation',{}).get('available','-- nicht versucht'),'warnings=',a['warnings'],'notes=',a.get('capability_notes'))
