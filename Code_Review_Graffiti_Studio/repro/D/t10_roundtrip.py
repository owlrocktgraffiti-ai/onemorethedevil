"""Zusatz: Verlust durch Farbraum-Rundreisen in render() (YCbCr für Tonwerte, HSV für Lebendigkeit) bei neutralen Operationen."""
import numpy as np
from PIL import Image
import common
v=np.arange(0,256,3,dtype=np.uint8);r,g,b=np.meshgrid(v,v,v,indexing='ij')
a=np.stack([r,g,b],-1).reshape(1,-1,3);im=Image.fromarray(a)
y=im.convert('YCbCr').convert('RGB');h=im.convert('HSV').convert('RGB')
for name,o in [('YCbCr',y),('HSV',h)]:
    d=np.abs(np.array(o).astype(int)-a.astype(int)).max(axis=2)
    print(f'{name}-Rundreise: max {d.max()} Stufen, Mittel {d.mean():.2f}, Anteil >=3 Stufen {(d>=3).mean()*100:.1f} %, >=6 Stufen {(d>=6).mean()*100:.2f} %')
    i=d.argmax();print('   schlimmstes Beispiel',a[0,i],'->',np.array(o)[0,i])
