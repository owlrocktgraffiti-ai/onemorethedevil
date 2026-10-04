# D1: ICC-Profil beim Lesen/Speichern
from common import *
import io,numpy as np
from PIL import Image,ImageCms
from adjustments import Settings,render,CONTROL_SPEC
import graffiti
from studio_backend import render_one
# Ein echtes, von ImageCms erzeugtes Profil als "Fremdprofil": LAB->RGB geht nicht; wir bauen ein P3-artiges Profil ueber createProfile nicht moeglich,
# daher: wir nehmen die Bytes eines sRGB-Profils als Platzhalter fuer Existenz-Test, und fuer die Farbwirkung Display-P3-Matrix analytisch.
srgb=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
a=np.zeros((600,800,3),np.uint8);a[:]=(120,110,100);a[100:300,100:400]=(220,40,40);a[300:500,400:700]=(40,200,60)
a=(a.astype(int)+np.random.default_rng(1).integers(-6,7,a.shape)).clip(0,255).astype(np.uint8)
src=OUT/'icc_src.jpg';Image.fromarray(a).save(src,quality=95,icc_profile=srgb)
im=graffiti.read_image(src);print('read_image info icc:',len(im.info.get('icc_profile') or b''),'B')
base={k:0 for k in CONTROL_SPEC}
for name,ch in [('neutral',{}),('contrast10',{'contrast':10}),('exposure10',{'exposure':10}),('temperature20',{'temperature':20}),('vibrance50',{'vibrance':50}),('sharp50',{'sharpness':50}),('denoise30',{'denoise':30})]:
    v=dict(base,**ch);r=render(im,v);print(f'render {name:14s} icc={len(r.info.get("icc_profile") or b"")} B')
for prof in ['originalnah','kraeftig','nacht','auto']:
    for prev in (True,False):
        res=render_one(src,OUT/f'icc_{prof}_{prev}.png',Settings(profile=prof,mode='klassisch'),preview=prev)
        with Image.open(res['image']) as o:print(f'render_one profile={prof:11s} preview={prev!s:5s} look={res["analysis"].get("look")} icc={len(o.info.get("icc_profile") or b"")} B')
# Farbwirkung: P3-Zahlen als sRGB interpretiert (analytisch, Standardmatrizen)
def lin(c):c=c/255;return np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)
def enc(c):return np.where(c<=.0031308,12.92*c,1.055*np.clip(c,0,None)**(1/2.4)-.055)
P3=np.array([[0.4865709,0.2656677,0.1982173],[0.2289746,0.6917385,0.0792869],[0,0.0451134,1.0439444]])
SR=np.array([[0.4124564,0.3575761,0.1804375],[0.2126729,0.7151522,0.0721750],[0.0193339,0.1191920,0.9503041]])
def lab(xyz):
    w=np.array([0.95047,1,1.08883]);t=xyz/w;f=np.where(t>216/24389,np.cbrt(t),(24389/27*t+16)/116)
    return np.array([116*f[1]-16,500*(f[0]-f[1]),200*(f[1]-f[2])])
for c in [(220,40,40),(40,200,60)]:
    x=np.array(c,float);xyz_p3=P3@lin(x);xyz_s=SR@lin(x)
    L1=lab(xyz_p3);L2=lab(xyz_s);corr=np.round(enc(np.linalg.solve(SR,xyz_p3)).clip(0,1)*255)
    print(c,'als P3 korrekt in sRGB ~',corr,'dE76 bei Anzeige als sRGB=%.1f'%np.linalg.norm(L1-L2),'Chroma P3=%.1f sRGB-Anzeige=%.1f'%(np.hypot(*L1[1:]),np.hypot(*L2[1:])))
