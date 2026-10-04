"""K8: Entartete Ecken (zwei Ecken auf demselben Punkt, z. B. beide an den Bildrand gezogen und dort geklemmt,
oder drei Ecken auf einer Linie) bestehen die Prüfung; Ergebnis prüfen."""
import sys
from pathlib import Path
K=Path(__file__).resolve().parent;sys.path.insert(0,str(K/'Resources'))
import numpy as np,cv2
from PIL import Image
from adjustments import Settings
from photo_prepare import transform
im=Image.fromarray((np.random.default_rng(2).random((900,1200,3))*200+30).astype(np.uint8))
cases={'doppelte Ecke (TR=BR)':[[0,0],[1,0],[1,0],[0,1]],
       'doppelte Ecke (TL=TR)':[[1,0],[1,0],[1,1],[0,1]],
       'drei Punkte kollinear':[[0,0],[0.5,0],[1,0],[0,1]],
       'alle auf einer Linie':[[0,0],[0.3,0.3],[0.6,0.6],[1,1]],
       'Ecke 2 auf Kante 1-3':[[0,0],[0.5,0.5],[1,1],[0,1]]}
for name,c in cases.items():
    try:Settings(corners=c);valid='Settings OK'
    except Exception as e:valid='Settings-Fehler: '+str(e)
    try:
        out=transform(im,dict(corners=c,rotate=0));a=np.array(out)
        res=f'transform -> {out.size}, Mittelwert {a.mean():.1f}, Anteil schwarz {(a.max(axis=2)==0).mean():.2f}'
    except Exception as e:res='transform-Fehler: '+type(e).__name__+': '+str(e)[:120]
    print(f'{name:24s} | {valid:40s} | {res}')
