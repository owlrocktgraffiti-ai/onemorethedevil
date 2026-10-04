"""K2: Schalter 'Automatische Papierkanten' (geometry='aus') wirkt nicht mehr, sobald knobs.corners gesetzt sind
(openMask setzt sie immer, es gibt keinen Weg zurück auf nil)."""
import json,subprocess,sys,os
from pathlib import Path
from PIL import Image
K=Path(__file__).resolve().parent;R=K/'Resources';OUT=K/'out'
def bridge(cmd,req):
    q=OUT/f'k2_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(R/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True,env=dict(os.environ,OCR_STUB_MODE='none'))
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
src=OUT/'c_wand.jpg'
corners=[[0.2,0.2],[0.8,0.2],[0.8,0.8],[0.2,0.8]]  # z. B. aus plan['preparation'] eines falsch erkannten "Abzugs" übernommen
for geo in ('auto','aus'):
    r=bridge('preview',dict(source=str(src),output=str(OUT/f'k2_{geo}.png'),settings=dict(mode='klassisch',geometry=geo,corners=corners,use_saved_retouches=False)))
    a=r['result']['analysis']
    with Image.open(r['result']['image']) as im:print(f"geometry={geo:4s} -> Vorschau {im.size}, preparation.corners={a['preparation']['corners']}")
with Image.open(src) as im:print('Original',im.size)
