"""Hinweis 4 + eigene Prüfung: Kennzeichnung generativer Referenzkorrekturen und veraltete Warnungen."""
from common import *
import json,hashlib,shutil,subprocess,sys,csv
from pathlib import Path
import analysis,graffiti
from adjustments import Settings
# Eigene Kopie, damit Bekannte_Retuschen.json verändert werden darf
R4=E/'Resources_e4';shutil.rmtree(R4,ignore_errors=True);shutil.copytree(RES,R4,ignore=shutil.ignore_patterns('__pycache__'))
# Synthetisches "WFTPXN": Graffiti-Fläche mit zentralem Blitzfleck
rng=np.random.default_rng(11);h,w=900,1200;yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
a=np.stack([110+70*np.sin(xx/31.),70+60*np.cos(yy/19.),150+50*np.sin((xx-yy)/43.)],-1)+rng.normal(0,5,(h,w,1))
r=np.hypot(xx-w/2,yy-h/2);a+=np.clip(1.4-r/120,0,1)[...,None]*255
src_img=Image.fromarray(np.clip(a,0,255).astype(np.uint8));src=OUT/'e4_blitz.jpg';src_img.save(src,quality=92)
ref=Image.fromarray(np.clip(a-np.clip(1.4-r/120,0,1)[...,None]*255,0,255).astype(np.uint8))
(R4/'Referenzkorrekturen').mkdir(exist_ok=True);rp=R4/'Referenzkorrekturen/Korrektur_99.png';ref.save(rp)
fp=analysis.digest_image(graffiti.read_image(src))
rec=json.loads((R4/'Bekannte_Retuschen.json').read_text())
rec.append(dict(source_name=src.name,image_sha256=fp,cached='Referenzkorrekturen/Korrektur_99.png',cached_sha256=hashlib.sha256(rp.read_bytes()).hexdigest(),description='Test: KI-Einzelretusche',generative_reconstruction=True))
(R4/'Bekannte_Retuschen.json').write_text(json.dumps(rec,indent=2,ensure_ascii=False))
def bridge(cmd,req):
    q=OUT/f'e4_{cmd}_req.json';q.write_text(json.dumps(req))
    p=subprocess.run([sys.executable,str(R4/'native_bridge.py'),cmd,'--request',str(q)],capture_output=True,text=True)
    ev=[json.loads(l) for l in p.stdout.splitlines() if l.strip()];return ev[-1]
# (a) Vorschau mit Standardeinstellungen (wie App-Start)
res=bridge('preview',dict(source=str(src),output=str(OUT/'e4_prev.png'),settings={}))['result'];pl=res['analysis']
print('(a) Vorschau: warnings[0] (UI zeigt nur diese) =',pl['warnings'][:1],'| effective_backend =',pl['effective_backend'],'-> Statuszeile "Vorschau fertig · Klassisch"')
# (b) Einzel-Export: Dateiname, PNG-Metadaten
out=OUT/'e4_export';shutil.rmtree(out,ignore_errors=True);Path(str(out)+'.zip').unlink(missing_ok=True)
res=bridge('export',dict(source=str(src),output=str(out/'e4_blitz.png'),settings=dict(export='instagram')))['result']
with Image.open(res['image']) as im:print('(b) Export-Datei:',Path(res['image']).name,'PNG-Info/Text-Chunks:',dict(im.info),'| Instagram:',sorted(p.name for p in (out/'Instagram').iterdir()))
# (c) Ordner-Export: Protokoll.csv
out2=OUT/'e4_batch';shutil.rmtree(out2,ignore_errors=True);Path(str(out2)+'.zip').unlink(missing_ok=True)
res=bridge('batch',dict(files=[str(src)],output=str(out2),settings={}))['result']
print('(c) Stapel UI-Warnungen:',res['warnings'],'| CSV:',list(csv.reader(open(out2/'Protokoll.csv',encoding='utf-8-sig')))[1][2:])
# (d) Einzelretusche AUS (Schalter "Bekannte Einzelretuschen" bzw. nach Ecken/Maske): veraltete Warnungen
res=bridge('preview',dict(source=str(src),output=str(OUT/'e4_prev_off.png'),settings=dict(use_saved_retouches=False)))['result'];pl=res['analysis']
print('(d) use_saved_retouches=False: cached_correction im Plan:', 'cached_correction' in pl,'| executed:',pl['executed'])
print('    warnings:',pl['warnings'],'| review_regions:',pl.get('review_regions'),'| Blitz-Kandidaten im Merkmalsbefund:',len(pl['features']['flash_check']['hotspots']),len(pl['features']['hotspot_candidates']))
# Vergleich: dasselbe Bild ohne registrierte Referenz
pl2=analysis.analyze(graffiti.read_image(src),Path('anders.jpg'),ocr=False)
print('    zum Vergleich ohne Referenz-Eintrag: warnings =',pl2['warnings'])
res=bridge('preview',dict(source=str(src),output=str(OUT/'e4_prev_rot.png'),settings=dict(rotation=0)))['result'];pl=res['analysis']
print('(e) Drehung 0° gesetzt: cached_correction:', 'cached_correction' in pl,'| warnings:',pl['warnings'])
# (f) Referenzfoto, das zugleich eine Papierkante liefert: KI-Hinweis ist nicht mehr warnings[0]
src2=OUT/'e1_gelbe_flaeche.jpg'
fp2=analysis.digest_image(graffiti.read_image(src2))
rec=json.loads((R4/'Bekannte_Retuschen.json').read_text());rec.append(dict(rec[-1],source_name=src2.name,image_sha256=fp2));(R4/'Bekannte_Retuschen.json').write_text(json.dumps(rec,indent=2,ensure_ascii=False))
res=bridge('preview',dict(source=str(src2),output=str(OUT/'e4_prev_f.png'),settings={}))['result'];pl=res['analysis']
print('(f) Referenz + Papierkanten-Kandidat: warnings[0] =',pl['warnings'][0],'| KI-Hinweis an Position',pl['warnings'].index('Die hinterlegte Einzelretusche enthält KI-rekonstruierte Details.'))
