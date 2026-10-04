# D5: jede Vorschau (neuer Prozess wie in der App) startet die KI erneut
from common import *
import numpy as np,json,subprocess,time,os,sys
from PIL import Image
rng=np.random.default_rng(5)
Image.fromarray(rng.integers(0,255,(1350,1080,3),dtype=np.uint8)).save(OUT/'insta.jpg')
log=OUT/'stub_calls.log';log.unlink(missing_ok=True)
env=dict(os.environ,STUB_MODE='slowfail',STUB_SLEEP='3',STUB_LOG=str(log))
for i in range(3):
    req=OUT/f'req{i}.json';req.write_text(json.dumps(dict(source=str(OUT/'insta.jpg'),output=str(OUT/f'prev{i}.png'),settings={})))
    t=time.time();r=subprocess.run([sys.executable,str(RES/'native_bridge.py'),'preview','--request',str(req)],capture_output=True,text=True,env=env)
    res=[json.loads(l) for l in r.stdout.splitlines() if l.startswith('{')];fin=[x for x in res if x['type'] in('result','error')][-1]
    an=fin.get('result',{}).get('analysis',{})
    print(f'Vorschau {i+1}: {time.time()-t:.1f}s',fin['type'],'size',an.get('output_size'),'backend',an.get('effective_backend'),'warn',[w for w in an.get('warnings',[]) if 'KI' in w])
print('Stub-Aufrufe:',log.read_text().split())
