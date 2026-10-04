"""D4: Vorschau startet im Automatikmodus das neuronale Modell; SESSION gilt nur pro Prozess,
die App startet pro Vorschau einen neuen Prozess -> fehlerhafte KI wird bei JEDER Vorschau erneut gestartet."""
import os,sys,json,subprocess,time,shutil
from pathlib import Path
import numpy as np
from PIL import Image
import common
RES=common.RES;OUT=common.OUT/'t4';OUT.mkdir(exist_ok=True)
engine=RES/'engine/realesrgan-ncnn-vulkan'
shutil.copy(common.HERE/'stubs/realesrgan_fail_slow.py',engine);os.chmod(engine,0o755)
rng=np.random.default_rng(4)
a=(rng.normal(0,25,(1350,1080,3))+np.array([120,110,100])).clip(0,255).astype(np.uint8)  # Instagram-Hochformat 1080x1350
src=OUT/'insta.jpg';Image.fromarray(a).save(src,quality=92)
log=OUT/'stub.log';log.unlink(missing_ok=True)
env=dict(os.environ,STUB_LOG=str(log),STUB_SLEEP=sys.argv[1] if len(sys.argv)>1 else '6')
py='/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/venv/bin/python'
for i,values in enumerate([{},{'contrast':20},{'contrast':30}],1):  # drei Reglerschritte = drei Vorschauen
    req=OUT/f'req{i}.json';req.write_text(json.dumps(dict(source=str(src),output=str(OUT/f'prev{i}.png'),settings=dict(values=values))))
    t=time.time();r=subprocess.run([py,str(RES/'native_bridge.py'),'preview','--request',str(req)],capture_output=True,text=True,env=env)
    final=[json.loads(l) for l in r.stdout.splitlines() if l.strip()][-1]
    res=final.get('result',{});an=res.get('analysis',{})
    print(f'Vorschau {i}: {time.time()-t:.1f}s, Ergebnis {Image.open(res["image"]).size if res else final}, backend={an.get("effective_backend")}, '
          f'Warnung KI={[w for w in an.get("warnings",[]) if "KI" in w]}')
print('KI-Starts laut Stub-Protokoll:',[json.loads(l)['input_size'] for l in log.read_text().splitlines()])
engine.unlink()
