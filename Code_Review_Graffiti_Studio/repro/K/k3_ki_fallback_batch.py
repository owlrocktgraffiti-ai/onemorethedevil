"""K3: Nach einem KI-Ausfall werden alle folgenden Fotos trotz Modus 'Lokale KI' ohne Warnung als OK geführt;
das Endergebnis an die App enthält keinen Hinweis."""
import json,subprocess,sys,os,shutil
from pathlib import Path
import numpy as np
from PIL import Image
K=Path(__file__).resolve().parent;R=K/'Resources';OUT=K/'out'
rng=np.random.default_rng(5)
files=[]
for i in range(3):
    p=OUT/f'k3_{i}.jpg';Image.fromarray((rng.random((600,800,3))*255).astype(np.uint8)).save(p);files.append(str(p))
out=OUT/'k3_batch'
if out.exists():shutil.rmtree(out)
q=OUT/'k3_req.json';q.write_text(json.dumps(dict(files=files,output=str(out),settings=dict(mode='ki',scale=2))))
p=subprocess.run([sys.executable,str(R/'native_bridge.py'),'batch','--request',str(q)],capture_output=True,text=True,env=dict(os.environ,OCR_FAIL_FIRST='0'))
ev=[json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
print('Ergebnis an die App: images=',ev['result']['images'],'warnings=',ev['result']['warnings'])
for line in (out/'Protokoll.csv').read_text(encoding='utf-8-sig').splitlines()[1:]:print('  CSV',line.split(',',1)[1])
for j in sorted(out.glob('0*.json')):
    a=json.loads(j.read_text());print(' ',j.name,'warnings=',a['warnings'],'| executed KI:',[x for x in a['executed'] if 'KI' in x])
