"""Hinweis 6 (Retusche): Ein-Punkt-Strich, Stärke 0/50/100, Wirkung nur innerhalb der Maske."""
import numpy as np,cv2
from PIL import Image
import common
from photo_prepare import transform
a=np.zeros((1000,1500,3),np.uint8);a[:]=(180,120,60);cv2.circle(a,(750,500),20,(0,0,0),-1)  # schwarzer Fleck = Störung
img=Image.fromarray(a)
for strength in (0,.5,1):
    cfg=dict(corners=[[0,0],[1,0],[1,1],[0,1]],rotate=0,glare_strength=0,retouch_strokes=[dict(points=[[750/1499,500/999]],radius=.03)],retouch_strength=strength)
    o=np.array(transform(img,cfg)).astype(int)
    outside=np.ones(a.shape[:2],bool);cv2.circle(outside.view(np.uint8),(750,500),31,0,-1)
    print(f'Stärke {strength}: Fleckmitte {o[500,750]} (Umgebung {a[100,100]}), max Änderung außerhalb Pinsel {np.abs(o-a)[outside.astype(bool)].max()}')
