# F1: _tkinter unimportierbar machen und preview/prepare/export ausfuehren
from common import *
shim=V/'work'/'notk';shim.mkdir(parents=True,exist_ok=True)
(shim/'_tkinter.py').write_text("raise ModuleNotFoundError(\"No module named '_tkinter'\",name='_tkinter')\n")
img=str(V/'test.jpg')
for cmd in ('preview','prepare','export'):
    out=V/'work'/f'v1_{cmd}'/'out.png'
    rc,ev,_,err,dt=bridge(cmd,dict(source=img,output=str(out),settings={}),{'PYTHONPATH':str(shim)})
    print(f'{cmd} ohne _tkinter: rc={rc} letztes Ereignis={ev[-1] if ev else None} | stderr-Ende={err.strip().splitlines()[-1] if err.strip() else ""!r}')
# Kontrolle mit tkinter
rc,ev,_,err,dt=bridge('preview',dict(source=img,output=str(V/'work'/'v1_ok'/'o.png'),settings={}))
print('preview mit _tkinter: rc',rc,'Endereignis',ev[-1]['type'] if ev else None)
r=subprocess.run([PY,'-c',f"import sys;sys.path.insert(0,{str(RES)!r});import graffiti;print('tkinter in sys.modules nach import graffiti:', 'tkinter' in sys.modules)"],capture_output=True,text=True);print(r.stdout.strip(),r.stderr[-200:])
