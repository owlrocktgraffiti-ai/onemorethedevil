from vcommon import *
import json,shutil,os
import graffiti,analysis
from studio_backend import render_one,batch_files
from adjustments import Settings
graffiti.SESSION.update(ocr_available=False,ai_available=False)
# E8: freigegebenes JPEG mit EXIF-Orientierung 6 (Pixel quer 600x400 -> Anzeige hochkant)
src=OUT/'v_frei.jpg';ex=Image.Exif();ex[0x0112]=6
px=Image.new('RGB',(600,400),(30,120,200));ImageDraw.Draw(px).rectangle((0,0,100,400),fill=(250,0,0));px.save(src,exif=ex,quality=95)
fp=analysis.digest_image(graffiti.read_image(src))
orig=(RES/'Freigegebene_Bilder.json').read_text();(RES/'Freigegebene_Bilder.json').write_text(json.dumps([dict(image_sha256=fp,description='t')]))
try:
    r=render_one(src,OUT/'v_e8_prev.png',Settings(values=dict(contrast=80,exposure=50)),True)
    print('E8 Vorschau Datei',Path(r['image']).name,'byte-identisch',Path(r['image']).read_bytes()==src.read_bytes(),'warnings',r['analysis']['warnings'])
    out=OUT/'v_e8_batch';shutil.rmtree(out,ignore_errors=True)
    if (OUT/'v_e8_batch.zip').exists():(OUT/'v_e8_batch.zip').unlink()
    batch_files([src],out,Settings(export='instagram'))
    with Image.open(next((out/'Instagram').rglob('Panorama_Gemeinsame_Basis.png'))) as b:
        arr=np.asarray(b.convert('RGB'));nonwhite=np.argwhere((arr<240).any(axis=2));(y0,x0),(y1,x1)=nonwhite.min(0),nonwhite.max(0)
        print('E8 Instagram-Basis Inhalt BxH',x1-x0+1,y1-y0+1,'(Anzeige hochkant 400x600)')
    with Image.open(out/'01_Vergleich.jpg') as v:
        arr=np.asarray(v.convert('RGB')).astype(int);print('E8 Vergleich links/rechts (blau-Spalten):', [int(((abs(arr[20:,s:e,2]-200)<40)&(arr[20:,s:e,0]<80)).any(axis=0).sum()) for s,e in ((0,390),(390,780))],'Hoehe:',[int(((abs(arr[20:,s:e,2]-200)<40)&(arr[20:,s:e,0]<80)).any(axis=1).sum()) for s,e in ((0,390),(390,780))])
finally:(RES/'Freigegebene_Bilder.json').write_text(orig)
# E11: langer Scan mit 2 weißen Stegen + Blitzfleck, Ordner-Export
a=np.full((600,2000,3),(80,100,70),np.uint8);a[:,650:665]=255;a[:,1330:1345]=255
yy,xx=np.mgrid[0:600,0:2000];r=np.hypot(xx-1000,yy-300);a=np.clip(a+np.clip(255*(1-r/60),0,255)[...,None],0,255).astype(np.uint8)
sp=OUT/'v_scan.png';Image.fromarray(a).save(sp);out=OUT/'v_e11';shutil.rmtree(out,ignore_errors=True)
if (OUT/'v_e11.zip').exists():(OUT/'v_e11.zip').unlink()
res=batch_files([sp],out,Settings());pl=json.loads((out/'01_v_scan.json').read_text())
print('E11 panel_candidates',len(pl.get('panel_candidates',[])),'review_regions',pl.get('review_regions'),'| Dateien',sorted(x.relative_to(out).as_posix() for x in out.rglob('*') if x.is_file()))
v=np.asarray(Image.open(out/'01_Vergleich.jpg').convert('RGB')).astype(int)
print('E11 gelbe Pixel im Vergleich',int(((v[:,:,0]>230)&(abs(v[:,:,1]-206)<25)&(v[:,:,2]<90)).sum()))
# E13: symmetrische Balken; Editor setzt Vollbild-Ecken + Region
n=np.random.default_rng(2).integers(30,200,(960,1440,3)).astype(np.uint8);n[:192]=0;n[-192:]=0
np_=OUT/'v_e13.png';Image.fromarray(n).save(np_)
r1=render_one(np_,OUT/'v_e13_a.png',Settings(),True)['analysis']['output_size']
r2=render_one(np_,OUT/'v_e13_b.png',Settings(corners=[[0,0],[1,0],[1,1],[0,1]],glare_regions=[[.4,.4,.5,.5]]),True)['analysis']
print('E13 vor Editor',r1,'nach Editor',r2['output_size'],'warnings',r2['warnings'])
