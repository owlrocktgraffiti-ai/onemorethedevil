"""Fingerabdruck mit Pillow 10.0.1 (separat installiert) vs. aktueller Pillow: gleiche Datei."""
import sys,hashlib,subprocess
from pathlib import Path
E=Path(__file__).resolve().parent
code='''import sys,hashlib
from PIL import Image,ImageOps
import PIL
for f in sys.argv[1:]:
    with Image.open(f) as im:
        r=ImageOps.exif_transpose(im).convert("RGB")
    print(PIL.__version__,Path(f).name if False else f.split("/")[-1],hashlib.sha256(r.convert("RGB").tobytes()).hexdigest()[:16])
'''
files=[str(E/'out'/x) for x in ('e2_12mp.jpg','e3_prog.jpg','e3_exif6.jpg')]
print(subprocess.run([sys.executable,'-c',code,*files],capture_output=True,text=True).stdout)
print(subprocess.run([sys.executable,'-c','import sys;sys.path.insert(0,"%s");'%(E/'oldpil')+code,*files],capture_output=True,text=True))
