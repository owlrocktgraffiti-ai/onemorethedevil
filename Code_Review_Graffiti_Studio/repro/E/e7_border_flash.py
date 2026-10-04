"""Hinweis 7: black_border schneidet echte (dunkle) Bildbereiche ab; weiße Farbe -> Blitzwarnung; weiße Zugstreifen -> Scan-Trenner."""
from common import *
import json
import analysis,graffiti
from studio_backend import render_one
from adjustments import Settings
rng=np.random.default_rng(4)
def night(top=0,bottom=0,left=0,right=0,h=1000,w=1500):
    a=np.clip(rng.normal(40,25,(h,w,3)),4,255).astype(np.uint8)      # schwach beleuchteter Zug
    a[200:700,300:1200]=np.clip(rng.normal(150,40,(500,900,3)),0,255).astype(np.uint8)  # beleuchtetes Piece
    # unbeleuchteter Nachthimmel/Schotter: echte Bildbereiche, aber Sensorwerte 0..3
    if top:a[:top]=rng.integers(0,4,(top,w,3))
    if bottom:a[h-bottom:]=rng.integers(0,4,(bottom,w,3))
    if left:a[:,:left]=rng.integers(0,4,(h,left,3))
    if right:a[:,w-right:]=rng.integers(0,4,(h,right,3))
    return Image.fromarray(a)
for name,kw in [('symmetrisch_200_200',dict(top=200,bottom=200)),('asymmetrisch_1_550',dict(top=1,bottom=550)),('seitlich_1_400',dict(left=1,right=400))]:
    im=night(**kw);p=OUT/f'e7_nacht_{name}.png';im.save(p)
    pl=analysis.analyze(graffiti.read_image(p),p,ocr=False)
    graffiti.SESSION.update(ocr_available=False,ai_available=True)
    r=render_one(p,OUT/f'e7_nacht_{name}_export.png',Settings(mode='klassisch',scale=1),False)
    with Image.open(r['image']) as o:size=o.size
    print(f'{name:22s} border_crop={pl.get("border_crop")} Original {im.size} -> Export {size}; warnings={[w for w in r["analysis"]["warnings"] if "Rand" in w or "Balken" in w]} executed={r["analysis"]["executed"][0]}')
# Weiße Farbe: große, gefüllte weiße Buchstaben (kein Blitz)
a=np.zeros((900,1200,3),np.uint8);a[:]=(40,60,140)
d=ImageDraw.Draw(im:=Image.fromarray(a))
for i,x in enumerate(range(150,1000,220)):d.rectangle((x,300,x+150,600),fill=(255,255,255),outline=(0,0,0),width=8)
p=OUT/'e7_weisse_buchstaben.png';im.save(p)
pl=analysis.analyze(graffiti.read_image(p),p,ocr=False)
print('weiße Buchstaben: starke Blitz-Spots=',[ (s['confidence'],s['kind']) for s in pl['features']['flash_check']['hotspots']][:4],'\n  warnings=',pl['warnings'],'\n  automatic_removal=',{s['automatic_removal'] for s in pl['features']['flash_check']['hotspots']})
r=render_one(p,OUT/'e7_weisse_export.png',Settings(mode='klassisch',scale=1),False)
o=np.array(Image.open(r['image']).convert('RGB'));print('  weiße Flächen nach Export noch weiß (Mittel im Buchstaben):',o[350:550,170:280].mean().round(1))
# Panorama-Zug mit durchgehendem weißen Zierstreifen
a=np.clip(rng.normal(120,30,(600,2400,3)),0,255).astype(np.uint8);a[300:312]=255
p=OUT/'e7_zug_streifen.png';Image.fromarray(a).save(p)
pl=analysis.analyze(graffiti.read_image(p),p,ocr=False)
print('Zug mit weißem Streifen: panel_candidates=',pl.get('panel_candidates'),'| warnings enthält Scan-Hinweis:',any('mehreren Fotos' in w for w in pl['warnings']))
