"""Gegenprobe: Sonderzeichen in Dateinamen im Ordnerexport (kein Fehler erwartet)."""
import json,subprocess,sys,os,shutil,zipfile
from pathlib import Path
import numpy as np
from PIL import Image
K=Path(__file__).resolve().parent;R=K/'Resources';OUT=K/'out'/'k7';shutil.rmtree(OUT,ignore_errors=True);OUT.mkdir(parents=True)
names=['Zug ü \'x\' "y" <b>&amp;.jpg','😀 emoji.jpg','Züg NFD.jpg','zeile\numbruch.jpg','-strich.jpg','punkt..jpg']
files=[]
for i,n in enumerate(names):
    p=OUT/n;Image.fromarray((np.random.default_rng(i).random((300,400,3))*255).astype(np.uint8)).save(p,format='JPEG');files.append(str(p))
out=OUT/'Ergebnis';q=OUT/'req.json';q.write_text(json.dumps(dict(files=files,output=str(out),settings=dict(mode='klassisch',scale=1,export='instagram'))))
p=subprocess.run([sys.executable,str(R/'native_bridge.py'),'batch','--request',str(q)],capture_output=True,text=True,env=dict(os.environ,PYTHONIOENCODING='utf-8'))
ev=[json.loads(l) for l in p.stdout.splitlines() if l.strip()]
print(ev[-1]['type'],ev[-1].get('result',{}).get('images'),ev[-1].get('message'))
print(sorted(x.name for x in out.iterdir()))
with zipfile.ZipFile(str(out)+'.zip') as z:print(len(z.namelist()),'Einträge im ZIP')
