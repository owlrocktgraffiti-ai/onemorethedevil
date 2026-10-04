"""OCR-Drehung (plan['rotation']) bzw. border_crop gehen verloren, sobald der Maskeneditor Ecken setzt (openMask übernimmt nur preparation.rotate)."""
import json,subprocess,sys,os
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parent;R=E/'Resources_ocr';OUT=E/'out'
def bridge(cmd,req,mode='rot90'):
    q=OUT/f'e11_{cmd}_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(R/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True,env=dict(os.environ,OCR_STUB_MODE=mode))
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
src=OUT/'e1_a_normal.jpg'
r1=bridge('preview',dict(source=str(src),output=str(OUT/'e11_a.png'),settings=dict(mode='klassisch')))['result']
# Swift openMask(): plans[..]['preparation'] fehlt -> corners=[[0,0],[1,0],[1,1],[0,1]], rotation=nil; Maskenbild und Rendern danach:
knobs=dict(mode='klassisch',corners=[[0,0],[1,0],[1,1],[0,1]],glare_regions=[[0.1,0.1,0.3,0.3]])
m=bridge('prepare',dict(source=str(src),output=str(OUT/'e11_mask.png'),settings=knobs))['result']
r2=bridge('preview',dict(source=str(src),output=str(OUT/'e11_b.png'),settings=dict(knobs,use_saved_retouches=False)))['result']
for name,p in (('Vorschau vor Maskeneditor',r1['image']),('Maskenbild im Editor',m['image']),('Vorschau nach "Übernehmen"',r2['image'])):
    with Image.open(p) as im:print(f'{name:28s} {im.size} {"hochkant" if im.height>im.width else "quer"}')
print('rotation im Plan nach Editor:',r2['analysis'].get('rotation'),'| warnings:',r2['analysis']['warnings'])
# ohne OCR-Stub: border_crop (schwarze Balken) kehrt nach dem Maskeneditor zurück
R=E/'Resources'
src=OUT/'e7_nacht_symmetrisch_200_200.png'
r1=bridge('preview',dict(source=str(src),output=str(OUT/'e11_c.png'),settings=dict(mode='klassisch')),'none')['result']
r2=bridge('preview',dict(source=str(src),output=str(OUT/'e11_d.png'),settings=dict(mode='klassisch',corners=[[0,0],[1,0],[1,1],[0,1]],glare_regions=[[0.1,0.1,0.3,0.3]],use_saved_retouches=False)),'none')['result']
with Image.open(r1['image']) as a,Image.open(r2['image']) as b:print('border_crop: vor Editor',a.size,'| nach Editor',b.size)
