"""Gegenprobe zu D9: Erzeugt manuelle Geometrie bei Reflexregler 'Auto' eine globale Schleierentfernung?"""
import sys;from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K/'Resources'))
from adjustments import Settings
plan=dict(look='kraeftig',features=dict(cast_suspected=False),warnings=[],preparation=None)
for kw in (dict(corners=[[0,0],[1,0],[1,1],[0,1]]),dict(rotation=0),dict(corners=[[0,0],[1,0],[1,1],[0,1]],values=dict(glare=50))):
    p,c=Settings(**kw).prepare_plan(plan);print(kw,'-> glare_strength',p['preparation']['glare_strength'],'| warnings',p['warnings'])
