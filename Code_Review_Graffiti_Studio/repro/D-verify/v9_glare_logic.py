# D9: Drehung 0 / Vollbild-Ecken schalten globale Schleierminderung ein; Bereich bei Auto wirkungslos
from common import *
import numpy as np
from PIL import Image
from adjustments import Settings
from studio_backend import render_one
rng=np.random.default_rng(9)
a=np.clip(rng.normal(150,25,(900,1200,3)),0,255).astype(np.uint8)  # Wandfoto ohne Papierkanten
a[200:700,300:900]=(240,240,235)  # weisse Farbe
Image.fromarray(a).save(OUT/'wall.jpg',quality=95)
neutral={'sharpness':0,'clarity':0,'denoise':0,'vibrance':0,'shadows':0,'contrast':0}
def run(tag,**kw):
    r=render_one(OUT/'wall.jpg',OUT/f'wall_{tag}.png',Settings(mode='klassisch',scale=1,**kw));o=np.array(Image.open(r['image']),np.float32)
    an=r['analysis'];return o,an
o0,a0=run('ref',values=dict(neutral,glare=50))
print('glare=50 ohne Geometrie: Mittel %.1f'%o0.mean(),'prep',a0.get('preparation'),'Warn',[w for w in a0['warnings'] if 'Reflex' in w])
o1,a1=run('rot0',values=dict(neutral,glare=50),rotation=0)
print('glare=50 + Drehung 0: Mittel %.1f mittl.|Diff| %.1f, weisse Flaeche %.1f -> %.1f'%(o1.mean(),np.abs(o1-o0).mean(),o0[200:700,300:900].mean(),o1[200:700,300:900].mean()),'Warn',[w for w in a1['warnings'] if 'Reflex' in w])
o2,a2=run('corners',values=dict(neutral,glare=50),corners=[[0,0],[1,0],[1,1],[0,1]])
print('glare=50 + Vollbild-Ecken (openMask): Mittel %.1f'%o2.mean())
o3,a3=run('regauto',values=neutral)
o4,a4=run('reg',values=neutral,glare_regions=[[.25,.2,.75,.8]])
print('Bereich markiert, Regler Auto: controls.glare',a4['controls']['glare'],'glare_strength',a4['preparation']['glare_strength'],'max|Diff| zu ohne Bereich',np.abs(o4-o3).max(),'Warn',a4['warnings'])
