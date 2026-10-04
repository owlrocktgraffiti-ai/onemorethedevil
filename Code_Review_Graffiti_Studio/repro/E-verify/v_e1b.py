from vcommon import *
import graffiti,analysis
from studio_backend import render_one
from adjustments import Settings
cases={'beton_outline14':dict(),'beton_outline25':dict(outline=25),'nacht_dunkel':dict(bg=(18,18,22),outline=20),'backstein_warm':dict(bg=(150,85,55),outline=20),'beton_rand5%':dict(margin=(0.05,0.06),outline=20)}
for k,kw in cases.items():
    im=wall(**kw);p=OUT/f'v_e1_{k}.png';im.save(p)
    pl=analysis.analyze(im,p,ocr=False)
    line=f'{k}: conf={pl.get("paper_confidence")} prep={bool(pl["preparation"])} warn={pl["warnings"][:2]}'
    if pl['preparation']:
        graffiti.SESSION['ocr_available']=False
        r=render_one(p,OUT/f'v_e1_{k}_out.png',Settings(),False);a=r['analysis']
        line+=f' | Export {im.size}->{a["output_size"]} exec0={a["executed"][0]!r} glare={a["preparation"]["glare_strength"]:.3f} warn={a["warnings"]}'
    print(line)
