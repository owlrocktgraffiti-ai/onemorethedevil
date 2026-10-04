"""D8: Wann erkennt scan_features einen Farbstich? Graue Wand mit zunehmendem Gelb-/Blaustich (+ Rauschen)."""
import numpy as np
from PIL import Image
import common
from analysis import scan_features
from adjustments import Settings, CONTROL_SPEC
rng=np.random.default_rng(8)
for noise in (2,6):
    row=[]
    for c in (0.02,0.04,0.06,0.08,0.10,0.12,0.15,0.20,0.30):
        base=np.array([140*(1+c),140,140*(1-c)])
        a=(np.ones((600,900,3))*base+rng.normal(0,noise,(600,900,3))).clip(0,255).astype(np.uint8)
        f=scan_features(Image.fromarray(a))
        m=a.reshape(-1,3).mean(0)
        row.append(f'R/B={m[0]/m[2]:.2f}:{"JA " if f["cast_suspected"] else "nein"} neutral={f["neutral_fraction"]:.2f}')
    print(f'Rauschen {noise}:',' | '.join(row))
# Schieberegler Weißabgleich 100 bei nicht erkanntem Stich
a=(np.ones((600,900,3))*np.array([160,140,115])).astype(np.uint8);f=scan_features(Image.fromarray(a))
plan=dict(features=f,look='kraeftig',white_balance_rgb=f['white_balance_rgb'],warnings=[],preparation=None)
p,c=Settings(values={'white_balance':100}).prepare_plan(plan)
print('Deutlicher Gelbstich (160,140,115): cast_suspected',f['cast_suspected'],'neutral_fraction',f['neutral_fraction'],'-> Regler Weißabgleich=100 ergibt Verstärkungen',p['white_balance_rgb'])
