# F9: Importzeit von vendor ohne .pyc + PYTHONDONTWRITEBYTECODE vs. vorkompiliert
import subprocess,sys,os,shutil,statistics,time,numpy,PIL,cv2,compileall
from pathlib import Path
V=Path(__file__).resolve().parent;PY=sys.executable
def fresh(dst):
    if dst.exists():shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for m in (numpy,PIL,cv2):
        src=Path(m.__file__).parent;shutil.copytree(src,dst/src.name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    for extra in Path(numpy.__file__).parent.parent.glob('*.libs'):shutil.copytree(extra,dst/extra.name)
    return dst
code="import sys,time;sys.path.insert(0,sys.argv[1]);t=time.perf_counter();import numpy,PIL.Image,cv2;assert numpy.__file__.startswith(sys.argv[1]);print(time.perf_counter()-t)"
def measure(vendor,env_extra):
    env=dict(os.environ);env.update(env_extra);r=[]
    for _ in range(5):r.append(float(subprocess.run([PY,"-c",code,str(vendor)],capture_output=True,text=True,env=env).stdout))
    return statistics.median(r)
a=fresh(V/'work'/'vendor_nopyc');print('ohne .pyc + DONTWRITEBYTECODE (wie App): %.3fs'%measure(a,{'PYTHONDONTWRITEBYTECODE':'1'}))
b=fresh(V/'work'/'vendor_pyc');compileall.compile_dir(str(b),quiet=1);print('vorkompiliert + DONTWRITEBYTECODE: %.3fs'%measure(b,{'PYTHONDONTWRITEBYTECODE':'1'}))
