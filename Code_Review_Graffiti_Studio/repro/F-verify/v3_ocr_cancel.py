# F3: Abbruch waehrend OCR (Stub schlaeft 12 s); SIGTERM bei 1.5 s, erneut SIGTERM/SIGINT bei 3 s/4 s
from common import *
import shutil
res=V/'work'/'Res_ocr'
if res.exists():shutil.rmtree(res)
shutil.copytree(RES,res)
stub=res/'engine'/'orientation';stub.write_text('#!/bin/sh\nsleep 12\necho "[]"\n');stub.chmod(0o755)
img=str(V/'test.jpg')
rc,ev,_,err,dt=bridge('preview',dict(source=img,output=str(V/'work'/'v3a'/'o.png'),settings={}),res=res)
print(f'ohne Abbruch: rc={rc} Dauer {dt:.2f}s Ende {ev[-1]["type"]}')
rc,ev,_,err,dt=bridge('preview',dict(source=img,output=str(V/'work'/'v3b'/'o.png'),settings={}),res=res,signals=[(1.5,signal.SIGTERM)])
print(f'SIGTERM bei 1.5s: rc={rc} Ende nach {dt:.2f}s (Latenz {dt-1.5:.2f}s) Ereignisse {[e["type"] if isinstance(e,dict) else e for e in ev]}')
rc,ev,_,err,dt=bridge('preview',dict(source=img,output=str(V/'work'/'v3c'/'o.png'),settings={}),res=res,signals=[(1.5,signal.SIGTERM),(3,signal.SIGTERM),(4,signal.SIGINT)])
print(f'3 Signale: rc={rc} Ende nach {dt:.2f}s Ende {ev[-1]["type"] if ev else None}')
# Wieviele OCR-Aufrufe pro Vorschau? Zaehlender Stub
cnt=V/'work'/'ocr_count.txt'
if cnt.exists():cnt.unlink()
stub.write_text(f'#!/bin/sh\necho x >> {cnt}\necho "[]"\n');stub.chmod(0o755)
for i in range(2):bridge('preview',dict(source=img,output=str(V/'work'/f'v3d{i}'/'o.png'),settings={}),res=res)
print('OCR-Aufrufe bei 2 Vorschauen:',len(cnt.read_text().split()))
