"""Hinweis 8 (Codepfad mit OCR-Stub): 'confident' OCR dreht beliebige Fotos bzw. bestätigt Papier-Zuschnitt ohne jede Warnung."""
import json,subprocess,sys,os
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parent;R=E/'Resources_ocr';OUT=E/'out'
def bridge(cmd,req,mode):
    q=OUT/f'e8_{cmd}_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(R/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True,env=dict(os.environ,OCR_STUB_MODE=mode))
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip()][-1]
# 1) Querformatiges Zugfoto (kein Abzug), Vision meldet sicher Text bei 90° (z. B. senkrechte Wagennummer/Werbung)
src=OUT/'e1_a_normal.jpg'
res=bridge('preview',dict(source=str(src),output=str(OUT/'e8_rot.png'),settings=dict(mode='klassisch')),'rot90')['result'];pl=res['analysis']
with Image.open(src) as a,Image.open(res['image']) as b:print('1) Zugfoto',a.size,'-> Vorschau',b.size,'| rotation=',pl.get('rotation'),'| warnings=',pl['warnings'],'| actions enthält Drehung:',[x for x in pl['actions'] if 'Drehung' in x])
# 2) Wandbild mit Rahmen (Papierkanten-Kandidat) + OCR "sicher" -> kein einziger Hinweis
src=OUT/'e1_wand_ohne_weiss.jpg'
res=bridge('preview',dict(source=str(src),output=str(OUT/'e8_wand.png'),settings=dict(mode='klassisch')),'up')['result'];pl=res['analysis']
with Image.open(src) as a,Image.open(res['image']) as b:print('2) Wandbild',a.size,'-> Vorschau',b.size,'| paper_confidence=',pl.get('paper_confidence'),'| warnings=',pl['warnings'],'| Status in der App: "Bereit", Filter-Typ wird "Abzüge"')
