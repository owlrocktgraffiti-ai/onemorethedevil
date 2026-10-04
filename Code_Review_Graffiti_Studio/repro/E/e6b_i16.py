"""16-Bit-Graustufen (PNG/TIFF): read_image -> convert('RGB') kappt statt zu skalieren (beide Pillow-Versionen)."""
import sys,subprocess,cv2,numpy as np
from pathlib import Path
E=Path(__file__).resolve().parent;D=E/'out'/'e6';D.mkdir(parents=True,exist_ok=True)
g=(np.tile(np.linspace(0,65535,400),(300,1))).astype(np.uint16)
cv2.imwrite(str(D/'I16_grau_16bit.png'),g);cv2.imwrite(str(D/'I16_grau_16bit.tif'),g)
code='''import sys,numpy as np,PIL
from PIL import Image,ImageOps
for f in sys.argv[1:]:
    with Image.open(f) as im:
        mode=im.mode;r=ImageOps.exif_transpose(im).convert("RGB")
    a=np.array(r)[...,0];print(PIL.__version__,f.split("/")[-1],mode,"Anteil Pixel=255:",round(float((a==255).mean()),3),"Mittelwert:",round(float(a.mean()),1),"(korrekt skaliert waere ~127)")
'''
files=[str(D/'I16_grau_16bit.png'),str(D/'I16_grau_16bit.tif')]
print(subprocess.run([sys.executable,'-c',code,*files],capture_output=True,text=True).stdout,end='')
print(subprocess.run([sys.executable,'-c','import sys;sys.path.insert(0,"%s");'%(E/'oldpil')+code,*files],capture_output=True,text=True).stdout,end='')
