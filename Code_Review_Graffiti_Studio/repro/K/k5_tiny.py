"""K5: Grenzwerte – winzige/ungewöhnliche Bilder durch Vorschau, Export und Maskenvorbereitung."""
import json,subprocess,sys,os
from pathlib import Path
import numpy as np
from PIL import Image
K=Path(__file__).resolve().parent;R=K/'Resources';OUT=K/'out'
def bridge(cmd,req):
    q=OUT/'k5_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(R/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True)
    ev=[json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    return (ev[-1] if ev else {'type':'KEIN EREIGNIS','stderr':p.stderr[-300:]})
for w,h in [(1,1),(2,2),(8,8),(40,30),(60,45),(3,400)]:
    p=OUT/f'k5_{w}x{h}.png';Image.fromarray((np.random.default_rng(1).random((h,w,3))*255).astype(np.uint8)).save(p)
    for cmd,st in [('preview',dict(mode='klassisch')),('export',dict(mode='klassisch')),('prepare',dict(corners=[[0,0],[1,0],[1,1],[0,1]]))]:
        out=OUT/f'k5_{cmd}_{w}x{h}'/'x.png'
        r=bridge(cmd,dict(source=str(p),output=str(out),settings=st))
        msg=r.get('message') or r.get('stderr') or ''
        size=''
        if r['type']=='result':
            with Image.open(r['result']['image']) as im:size=im.size
        print(f'{w}x{h} {cmd:8s} {r["type"]:8s} {size} {msg[:160]}')
