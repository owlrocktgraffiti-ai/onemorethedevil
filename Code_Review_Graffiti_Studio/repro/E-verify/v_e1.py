from vcommon import *
import graffiti,analysis
from studio_backend import render_one
from adjustments import Settings
im=wall();p=OUT/'v_e1_wand.png';im.save(p)
plan=analysis.analyze(im,p,ocr=False)
print('ocr=False: reason/paper_conf',plan.get('paper_confidence'),'prep',bool(plan['preparation']),'glare',(plan['preparation'] or {}).get('glare_strength'),'warnings',plan['warnings'])
plan=analysis.analyze(im,p,ocr=True)
print('ocr=True (Engine fehlt): orientation',plan.get('orientation'),'warnings',plan['warnings'])
graffiti.SESSION['ocr_available']=True
r=render_one(p,OUT/'v_e1_a.png',Settings(),True);a=r['analysis']
print('Vorschau 1 (frischer Prozess):',im.size,'->',a['output_size'],'warn',a['warnings'],'exec',a['executed'][:1])
r=render_one(p,OUT/'v_e1_b.png',Settings(),False);a=r['analysis']
print('Zweiter Aufruf im selben Prozess (Stapel-Situation): SESSION ocr',graffiti.SESSION['ocr_available'],'->',a['output_size'],'warn',a['warnings'])
