"""K1b: wie K1, aber mit als Abzug erkanntem Bild (paper_confidence>=.86): Vorschau dreht per OCR um 90°, der Ordnerexport nach einem OCR-Ausfall nicht – ohne Warnung."""
import json,subprocess,sys,os,shutil
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent;R=K/'Resources';OUT=K/'out'
def bridge(cmd,req,fail_first):
    q=OUT/f'k1b_{cmd}_req.json';q.write_text(json.dumps(req));ctr=OUT/'k1b_counter';ctr.write_text('0')
    p=subprocess.run([sys.executable,str(R/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True,env=dict(os.environ,OCR_COUNTER=str(ctr),OCR_FAIL_FIRST=fail_first))
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
r=bridge('preview',dict(source=str(OUT/'e_abzug.jpg'),output=str(OUT/'k1b_prev.png'),settings=dict(mode='klassisch')),'0')['result']
with Image.open(r['image']) as im:print('VORSCHAU e_abzug',im.size,'prep.rotate=',(r['analysis'].get('preparation') or {}).get('rotate'),'warnings=',r['analysis']['warnings'])
out=OUT/'k1b_batch';shutil.rmtree(out,ignore_errors=True);Path(str(out)+'.zip').unlink(missing_ok=True)
r=bridge('batch',dict(files=[str(OUT/'d_abzug.jpg'),str(OUT/'e_abzug.jpg')],output=str(out),settings=dict(mode='klassisch')),'1')
print('BATCH an App: warnings=',r['result']['warnings'])
for line in (out/'Protokoll.csv').read_text(encoding='utf-8-sig').splitlines()[1:]:print('  CSV',line.split(',',1)[1])
for j in sorted(out.glob('0*.json')):
    a=json.loads(j.read_text())
    with Image.open(a['output_path']) as im:print(' ',j.name,im.size,'prep.rotate=',(a.get('preparation') or {}).get('rotate'),'warnings=',a['warnings'])
