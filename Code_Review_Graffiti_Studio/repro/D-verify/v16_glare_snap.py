# D16: Auto-Reflexstaerke aus Rezept wird auf 10-%-Schritte gerundet
from common import *
from adjustments import Settings
for g in (.62,.15,.40):
    plan=dict(look='kraeftig',features={},warnings=[],actions=[],preparation=dict(corners=[[0,0],[1,0],[1,1],[0,1]],rotate=90,glare_strength=g))
    p,c=Settings().prepare_plan(plan);a=p['preparation']['glare_strength']
    print(f'Rezept {g}: Regler Auto={c["glare"]} -> angewandt {a:.3f} ({(a/g-1)*100:+.1f} %)')
