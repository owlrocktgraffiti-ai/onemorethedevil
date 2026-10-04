# D1-Ergaenzung: welche Pfade verlieren das Profil (KI-Pfad, Weissabgleich, transform)
from common import *
import os,numpy as np
from PIL import Image,ImageCms
from adjustments import Settings
from studio_backend import render_one
import graffiti
os.environ['STUB_MODE']='lanczos'
srgb=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
Image.fromarray(np.clip(np.random.default_rng(2).normal(120,20,(400,500,3)),0,255).astype(np.uint8)).save(OUT/'icc2.jpg',icc_profile=srgb)
neutral={'sharpness':0,'clarity':0,'denoise':0,'vibrance':0,'shadows':0,'contrast':0}
for tag,kw in [('neutral klassisch',dict(mode='klassisch',values=neutral)),('neutral KI',dict(mode='ki',scale=2,values=neutral)),('Ecken (transform)',dict(mode='klassisch',values=neutral,corners=[[.05,.05],[.95,.05],[.95,.95],[.05,.95]])),('Drehung 0',dict(mode='klassisch',values=neutral,rotation=0))]:
    graffiti.SESSION['ai_available']=True
    r=render_one(OUT/'icc2.jpg',OUT/'icc2_out.png',Settings(**kw))
    with Image.open(r['image']) as o:print(f'{tag:18s} backend={r["analysis"]["effective_backend"]:9s} icc={len(o.info.get("icc_profile") or b"")} B')
