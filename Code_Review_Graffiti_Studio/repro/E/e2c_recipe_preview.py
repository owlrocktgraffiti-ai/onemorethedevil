"""Vorschauzeit eines 12-MP-Fotos mit hinterlegtem Fotorezept (wie IMG_4363, App-Startfoto): jede Reglerbewegung."""
from common import *
import json,shutil,subprocess,sys,time
import analysis,graffiti
R=E/'Resources_e2';shutil.rmtree(R,ignore_errors=True);shutil.copytree(RES,R,ignore=shutil.ignore_patterns('__pycache__'))
big=graffiti.read_image(OUT/'e2_12mp.jpg').transpose(Image.Transpose.ROTATE_90);src=OUT/'e2c_IMG_4363.JPG';big.save(src,quality=90)
rec=json.loads((R/'Fotorezepte.json').read_text());entry=dict(rec['IMG_4363.JPG']);entry['image_sha256']=analysis.digest_image(graffiti.read_image(src));rec['e2c_IMG_4363.JPG']=entry
(R/'Fotorezepte.json').write_text(json.dumps(rec,indent=2))
for i,val in enumerate((10,20,30)):
    q=OUT/'e2c_req.json';q.write_text(json.dumps(dict(source=str(src),output=str(OUT/f'e2c_prev{i}.png'),settings=dict(values=dict(contrast=val)))))
    s=time.perf_counter();p=subprocess.run([sys.executable,str(R/'native_bridge.py'),'preview','--request',str(q)],capture_output=True,text=True)
    ev=[json.loads(l) for l in p.stdout.splitlines() if l.strip()]
    print(f'Kontrast {val} %: {time.perf_counter()-s:5.2f} s bis Ergebnis ({ev[-1]["type"]}, preparation={bool(ev[-1]["result"]["analysis"].get("preparation"))})')
