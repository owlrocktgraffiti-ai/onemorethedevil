from vcommon import *
import json,photo_prepare
f=RES/'Fotorezepte.json';orig=f.read_text()
try:
    seen={}
    def fake_review(image,cfg,name):seen['start']=cfg['corners'];return dict(corners=[[0,0],[1,0],[1,1],[0,1]],rotate=0,glare_strength=0)
    photo_prepare.review=fake_review
    other=Image.fromarray(np.random.default_rng(9).integers(0,255,(4032,3024,3),dtype=np.uint8))
    photo_prepare.prepare(other,'/anderer/Ordner/IMG_4363.JPG','pruefen')
    new=json.loads(f.read_text());old=json.loads(orig)
    print('Startecken = fremdes Rezept:',seen['start']==old['IMG_4363.JPG']['corners'])
    print('sha vorher',old['IMG_4363.JPG']['image_sha256'][:12],'nachher',new['IMG_4363.JPG']['image_sha256'][:12],'| Schlüssel',list(new))
finally:f.write_text(orig)
