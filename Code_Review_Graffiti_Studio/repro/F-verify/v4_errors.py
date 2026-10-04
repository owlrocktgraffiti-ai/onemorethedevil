# F4: Fehler ausserhalb des try (Settings), leere Meldungen, prepare-Fehler
from common import *
img=str(V/'test.jpg')
cases={'contrast=35':dict(values=dict(contrast=35)),'scale=3':dict(scale=3),
       'gekreuzte Ecken':dict(corners=[[0,0],[1,1],[1,0],[0,1]])}
for name,s in cases.items():
    for cmd in ('preview','prepare'):
        rc,ev,_,err,dt=bridge(cmd,dict(source=img,output=str(V/'work'/'v4'/'o.png'),settings=s))
        last=[l for l in err.strip().splitlines() if l.strip()][-1] if err.strip() else ''
        print(f'{name}/{cmd}: rc={rc} JSON-Ereignisse={len(ev)} stderr-Letzte={last!r}\n   Swift-Anzeige(2 Zeilen)={swift_display(err)!r}')
# prepare mit Ausschnitt zu klein (konvex, aber winzig)
rc,ev,_,err,dt=bridge('prepare',dict(source=img,output=str(V/'work'/'v4'/'p.png'),settings=dict(corners=[[0.5,0.5],[0.52,0.5],[0.52,0.52],[0.5,0.52]])))
print('prepare winzig:',rc,ev[-1] if ev else None)
for exc in (AssertionError(),MemoryError(),KeyboardInterrupt.__mro__[0]):
    pass
print('str(AssertionError())=',repr(str(AssertionError())),' str(MemoryError())=',repr(str(MemoryError())),' MemoryError ist Exception:',issubclass(MemoryError,Exception))
# Absturz per SIGSEGV
import shutil
res=V/'work'/'Res_segv'
if res.exists():shutil.rmtree(res)
shutil.copytree(RES,res)
p=res/'studio_backend.py';p.write_text(p.read_text().replace("def render_one(source,destination,settings=None,preview=False,cancel=None,progress=None):\n","def render_one(source,destination,settings=None,preview=False,cancel=None,progress=None):\n import ctypes;ctypes.string_at(0)\n",1))
rc,ev,_,err,dt=bridge('preview',dict(source=img,output=str(V/'work'/'v4'/'s.png'),settings={}),res=res)
print('SIGSEGV: rc',rc,'Ereignisse',[e['type'] for e in ev],'stderr',repr(err[-200:]))
