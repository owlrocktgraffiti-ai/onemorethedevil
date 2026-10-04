from vcommon import *
import io,traceback
import graffiti,analysis,flash
from studio_backend import render_one
from adjustments import Settings
graffiti.SESSION.update(ocr_available=False,ai_available=False)
def T(name,f):
    try:print(name,'->',f())
    except Exception as e:print(name,'-> FEHLER',type(e).__name__,str(e)[:150])
# E5: Nachtbild mit verrauschtem Schwarz 0..3 oben 2 Zeilen, unten 500 Zeilen
rng=np.random.default_rng(1);h,w=1000,1500
a=rng.integers(20,200,(h,w,3)).astype(np.uint8)
a[:2]=rng.integers(0,4,(2,w,3));a[500:]=rng.integers(0,4,(500,w,3))
night=Image.fromarray(a);T('E5 black_border asym 2/500',lambda:analysis.black_border(night))
p=OUT/'v_e5.png';night.save(p)
T('E5 render_one',lambda:(lambda r:(r['analysis']['output_size'],r['analysis']['warnings'],r['analysis']['executed'][0]))(render_one(p,OUT/'v_e5_out.png',Settings(scale=1),False)))
b=rng.integers(20,200,(h,w,3)).astype(np.uint8);b[:,:3]=0;b[:,1100:]=0
T('E5 black_border links3/rechts400',lambda:analysis.black_border(Image.fromarray(b)))
# E6: 16-bit grau
g=(np.tile(np.linspace(0,65535,800),(300,1))).astype(np.uint16)
import cv2;cv2.imwrite(str(OUT/'v_g16.png'),g);cv2.imwrite(str(OUT/'v_g16.tif'),g)
for f in ('v_g16.png','v_g16.tif'):
    with Image.open(OUT/f) as im:mode=im.mode
    T(f'E6 {f} mode={mode} read_image',lambda:(lambda x:(round(float(np.asarray(x).mean()),1),round(float((np.asarray(x)==255).mean()),3)))(graffiti.read_image(OUT/f)))
# E7: ICC
from PIL import ImageCms
prof=ImageCms.ImageCmsProfile(ImageCms.createProfile('LAB'))  # irgendein Nicht-sRGB-Profil, nur Durchreichung testen
icc=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
src=OUT/'v_icc.jpg';Image.new('RGB',(600,400),(200,40,40)).save(src,icc_profile=icc)
r=render_one(src,OUT/'v_icc_out.png',Settings(),False)
with Image.open(r['image']) as o:print('E7 Ausgabe icc_profile vorhanden:','icc_profile' in o.info,'| Quelle:',len(icc),'Bytes')
# E14
(OUT/'v_leer.jpg').write_bytes(b'');full=(OUT/'v_icc.jpg').read_bytes();(OUT/'v_halb.jpg').write_bytes(full[:len(full)//2])
for f in ('v_leer.jpg','v_halb.jpg'):T(f'E14 {f}',lambda:graffiti.read_image(OUT/f).size)
big=Image.new('L',(14000,13000));big.save(OUT/'v_big.png');del big
T('E14 182MP',lambda:graffiti.read_image(OUT/'v_big.png').size)
# E15
for s in [(5000,1),(1800,1),(1799,1),(2000,2)]:
    T(f'E15 {s}',lambda:bool(analysis.analyze(Image.new('RGB',s,(90,90,90)),Path('x.png'),ocr=False)))
# E16
pl=dict(look='kraeftig',features={},preparation=dict(corners=[[0,0],[1,0],[1,1],[0,1]],rotate=90,glare_strength=.62),warnings=[],actions=[])
T('E16 glare wirksam',lambda:Settings().prepare_plan(pl)[0]['preparation']['glare_strength'])
# E17 weiße Buchstaben
c=np.full((1000,1500,3),(40,60,90),np.uint8);im=Image.fromarray(c);d=ImageDraw.Draw(im)
for i in range(4):d.rectangle((300+i*230,350,460+i*230,650),fill=(255,255,255),outline=(0,0,0),width=8)
fc=flash.inspect(im);print('E17 spots',[(x['confidence'],x['kind']) for x in fc['hotspots']])
print('E17 warnings',analysis.analyze(im,Path('w.png'),ocr=False)['warnings'])
z=np.full((500,1600,3),(60,70,80),np.uint8);z[245:255]=255
print('E17 Zug-Streifen panel_candidates',analysis.print_separators(Image.fromarray(z)))
