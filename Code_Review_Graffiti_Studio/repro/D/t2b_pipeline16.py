"""D2b: 16-Bit-Graustufen-Scan und Float-TIFF komplett durch render_one (Export-Pfad der App)."""
import numpy as np, cv2
from PIL import Image
import common
from adjustments import Settings
from studio_backend import render_one
OUT=common.OUT/'t2'
rng=np.random.default_rng(0)
img=(np.tile(np.linspace(3000,60000,1200),(900,1))+rng.normal(0,800,(900,1200))).clip(0,65535).astype(np.uint16)
p=OUT/'scan16.png';cv2.imwrite(str(p),img)
for name,src in [('scan16.png',p),('float.tif',OUT/'float.tif')]:
    r=render_one(src,OUT/('ergebnis_'+name.replace('.','_')+'.png'),Settings(mode='klassisch'),preview=False)
    a=np.array(Image.open(r['image']).convert('L')).astype(float)
    print(name,'-> Ergebnis',Image.open(r['image']).size,'Mittel',a.mean().round(1),'Std',a.std().round(2),'Anteil 255:',(a>=255).mean().round(3),'Warnungen:',r['analysis']['warnings'],'Backend:',r['analysis']['effective_backend'])
