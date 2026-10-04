"""Zusatz: Auto-Wert des Reflexreglers wird aus dem Rezept abgeleitet und auf 10 % gerundet -> angewandte Stärke weicht vom Rezept ab."""
import json,common
from adjustments import Settings
rec=json.loads((common.RES/'Fotorezepte.json').read_text())['IMG_4363.JPG']
for g in (rec['glare_strength'],.15,.40):
    plan=dict(features={},look='kraeftig',warnings=[],preparation=dict(rec,glare_strength=g))
    p,c=Settings().prepare_plan(plan)
    print(f'Rezept glare_strength={g}: Regler Auto={c["glare"]} -> angewandt {p["preparation"]["glare_strength"]:.3f} ({(p["preparation"]["glare_strength"]/g-1)*100:+.1f} %)')
