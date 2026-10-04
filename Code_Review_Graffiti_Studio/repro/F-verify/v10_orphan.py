# F10: Modell-Stub laeuft nach SIGKILL der Bruecke weiter; nach SIGTERM nicht
from common import *
import shutil
res=V/'work'/'Res_model'
if res.exists():shutil.rmtree(res)
shutil.copytree(RES,res)
stub=res/'engine'/'realesrgan-ncnn-vulkan';stub.write_text('#!/bin/sh\nexec sleep 41.5\n');stub.chmod(0o755)
small=V/'work'/'small.jpg'
from PIL import Image
Image.open(V/'test.jpg').resize((600,450)).save(small)
def models():
    r=subprocess.run(['ps','-eo','pid,ppid,args'],capture_output=True,text=True).stdout
    return [l.split(None,2)[:2] for l in r.splitlines() if 'sleep 41.5' in l and 'grep' not in l]
for sig in (signal.SIGTERM,signal.SIGKILL):
    req=dict(source=str(small),output=str(V/'work'/'v10'/'o.png'),settings=dict(mode='ki',scale=2))
    rc,ev,_,err,dt=bridge('preview',req,res=res,signals=[(4,sig)])
    time.sleep(0.5);m=models()
    print(f'{sig.name} an Bruecke: rc={rc} Dauer {dt:.2f}s Ereignisse {[e["type"] for e in ev if isinstance(e,dict)][-2:]} | verbliebene Modellprozesse (pid,ppid)={m}')
    for pid,_ in m:os.kill(int(pid),signal.SIGKILL)
