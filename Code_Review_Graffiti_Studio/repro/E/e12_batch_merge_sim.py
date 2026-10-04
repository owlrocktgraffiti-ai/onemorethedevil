"""Simulation von StudioModel.exportLibrary() (GraffitiStudio.swift:147-150) in Python + echter batch-Aufruf.
Szenario: Nutzer schaltet bei Foto B 'Automatische Papierkanten' aus (Fehlzuschnitt), B bleibt ausgewählt, 'Ordner exportieren'.
Foto A (bekanntes Rezept wie IMG_4363) wurde vorher mit Standardwerten angesehen (perPhoto[A].geometry='auto')."""
import json,shutil,subprocess,sys,copy
from pathlib import Path
from PIL import Image
E=Path(__file__).resolve().parent;R=E/'Resources_e2';OUT=E/'out'
A=OUT/'e2c_IMG_4363.JPG';B=OUT/'e1_wand_ohne_weiss.jpg'
default=dict(values={},profile='auto',mode='klassisch',scale=1,geometry='auto',use_saved_retouches=True,export='fotos',glare_regions=[],retouch_strokes=[])
perPhoto={str(A):copy.deepcopy(default),str(B):dict(copy.deepcopy(default),geometry='aus')}
knobs=perPhoto[str(B)]  # ausgewähltes Foto
base=copy.deepcopy(knobs);base.pop('corners',None);base['glare_regions']=[];base['retouch_strokes']=[];base.pop('rotation',None)
specific={}
for path,saved in perPhoto.items():   # exakt die Felder, die Swift übernimmt
    m=copy.deepcopy(base);m['values'].update(saved['values'])
    for k in ('corners','rotation'):
        if k in saved:m[k]=saved[k]
    m['glare_regions']=saved['glare_regions'];m['retouch_strokes']=saved['retouch_strokes']
    if saved['profile']!='auto':m['profile']=saved['profile']
    if saved['mode']!='auto':m['mode']=saved['mode']
    if saved['scale']!=0:m['scale']=saved['scale']
    if not saved['use_saved_retouches']:m['use_saved_retouches']=False
    specific[path]=m   # geometry wird NIE aus saved übernommen
print('per_photo geometry:',{Path(k).name:v['geometry'] for k,v in specific.items()})
out=OUT/'e12_batch';shutil.rmtree(out,ignore_errors=True);Path(str(out)+'.zip').unlink(missing_ok=True)
q=OUT/'e12_req.json';q.write_text(json.dumps(dict(files=[str(A),str(B)],output=str(out),settings=base,per_photo=specific)))
p=subprocess.run([sys.executable,str(R/'native_bridge.py'),'batch','--request',str(q)],capture_output=True,text=True)
for f in sorted(out.glob('0*.json')):
    pl=json.loads(f.read_text());print(f.name,'preparation angewendet:',bool(pl.get('preparation')),'output_size',pl['output_size'],'(Vorschau mit eigenem Foto-Zustand: Rezept angewendet)')
