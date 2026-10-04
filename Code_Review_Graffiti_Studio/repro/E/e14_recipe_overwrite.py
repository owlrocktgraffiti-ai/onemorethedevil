"""CLI-Pfad 'Abzüge prüfen' (graffiti.py --prepare pruefen): Rezept wird unter dem Dateinamen gespeichert und
überschreibt das bekannte Rezept eines ANDEREN Fotos gleichen Namens; review() startet mit dessen Ecken."""
import sys,json,shutil
from pathlib import Path
E=Path(__file__).resolve().parent;R=E/'Resources_e14';shutil.rmtree(R,ignore_errors=True);shutil.copytree(E/'Resources',R,ignore=shutil.ignore_patterns('__pycache__'))
sys.path.insert(0,str(R))
import numpy as np
from PIL import Image
import photo_prepare
seen={}
def fake_review(image,cfg,title,parent=None):   # Tk-Dialog: Nutzer klickt sofort "So verarbeiten"
    seen['start_corners']=cfg['corners'];return dict(cfg)
photo_prepare.review=fake_review
before=json.loads((R/'Fotorezepte.json').read_text())['IMG_4363.JPG']
other=Image.fromarray(np.random.default_rng(1).integers(0,255,(4032,3024,3),dtype=np.uint8))  # anderes iPhone-Foto, gleicher Name+Größe
photo_prepare.prepare(other,'Neuer_Ordner/IMG_4363.JPG','pruefen')
after=json.loads((R/'Fotorezepte.json').read_text())['IMG_4363.JPG']
print('Startecken im Prüfdialog = Ecken des fremden Rezepts:',seen['start_corners']==before['corners'])
print('image_sha256 des bekannten IMG_4363-Rezepts vorher',before['image_sha256'][:12],'-> nachher',after['image_sha256'][:12])
print('Rezepte gesamt:',list(json.loads((R/'Fotorezepte.json').read_text())))
