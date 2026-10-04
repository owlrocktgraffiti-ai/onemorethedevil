# F12: DEFLATE vs STORED fuer bereits komprimierte PNG
import zipfile,time,numpy as np
from pathlib import Path
from PIL import Image
V=Path(__file__).resolve().parent;d=V/'work'/'v12';d.mkdir(parents=True,exist_ok=True)
rng=np.random.default_rng(0)
a=(rng.integers(0,255,(3000,4000,3))).astype('uint8');a[:, :2000]//=8
p=d/'bild.png';Image.fromarray(a).save(p,compress_level=1)
print('PNG MiB',round(p.stat().st_size/2**20,1))
for name,ct in (('DEFLATED',zipfile.ZIP_DEFLATED),('STORED',zipfile.ZIP_STORED)):
    z=d/f'{name}.zip';t=time.monotonic()
    with zipfile.ZipFile(z,'w',ct) as f:f.write(p,'bild.png')
    print(name,f'{time.monotonic()-t:.2f}s',round(z.stat().st_size/2**20,1),'MiB')
