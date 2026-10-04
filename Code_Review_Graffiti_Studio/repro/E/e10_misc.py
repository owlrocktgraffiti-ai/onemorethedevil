"""Diverse: Glare-Quantisierung gespeicherter Rezepte, veraltete Warnungen bei geometry='aus', Kleinbild mit Rahmen, Kosten transform 12 MP."""
from common import *
import json,time,copy
from pathlib import Path
import analysis,graffiti,photo_prepare
from adjustments import Settings
# 1) gespeichertes Rezept glare_strength 0.62 -> nach prepare_plan
rec=json.loads((RES/'Fotorezepte.json').read_text())['IMG_4363.JPG']
plan=dict(features=dict(cast_suspected=False),look='kraeftig',warnings=[],preparation=copy.deepcopy(rec),white_balance_rgb=[1,1,1])
p2,c=Settings().prepare_plan(plan)
print('1) Rezept glare_strength',rec['glare_strength'],'-> wirksam',round(p2['preparation']['glare_strength'],4),'(Regler',c['glare'],'%)')
# 2) Papierkanten-Kandidat, Benutzer schaltet "Automatische Papierkanten" aus
src=OUT/'e1_wand_grau.jpg';pl=analysis.analyze(graffiti.read_image(src),src,ocr=True)
p3,_=Settings(geometry='aus').prepare_plan(pl)
print('2) geometry=aus: preparation im Plan:',bool(p3.get('preparation')),'| warnings[0]:',p3['warnings'][0],'| actions:',[a for a in p3['actions'] if 'Papier' in a])
# 3) kleines Bild (90x90) mit Rahmen -> automatische Papierkante -> transform 'Ausschnitt zu klein'
im,_=wall_with_panel(size=(90,90),inset=(0.12,0.12),noise=1)
d=ImageDraw.Draw(im);d.rectangle((10,10,79,79),outline=(10,10,10),width=2)
p=OUT/'e10_klein90.png';im.save(p)
from studio_backend import render_one
try:
    r=render_one(p,OUT/'e10_klein_prev.png',Settings(mode='klassisch'),True);print('3) 90x90 OK',r['analysis'].get('paper_confidence'))
except Exception as e:print('3) 90x90 Vorschau FEHLER',type(e).__name__,e)
# 4) Kosten: bekanntes Rezept (Warp + Reflexminderung) auf voller 12-MP-Auflösung je Vorschau
big=graffiti.read_image(OUT/'e2_12mp.jpg').transpose(Image.Transpose.ROTATE_90)  # 3024x4032 wie IMG_4363
cfg=dict(rec,glare_strength=.595)
s=time.perf_counter();out=photo_prepare.transform(big,cfg);print(f'4) transform (Rezept IMG_4363) auf {big.size}: {time.perf_counter()-s:.2f} s -> {out.size}; danach erst Verkleinerung auf Vorschaugröße')
