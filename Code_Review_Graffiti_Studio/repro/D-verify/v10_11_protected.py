# D10/D11: freigegebene Bilder (Eintrag nur in der KOPIE, danach zurueckgesetzt)
from common import *
import numpy as np,json,shutil,filecmp
from PIL import Image
from analysis import digest_image
import graffiti
from adjustments import Settings
from studio_backend import render_one,batch_files
lock=RES/'Freigegebene_Bilder.json';orig=lock.read_text()
rng=np.random.default_rng(10)
a=rng.integers(0,255,(300,400,3),dtype=np.uint8);im=Image.fromarray(a)
ex=Image.Exif();ex[0x0112]=6
src=OUT/'prot.jpg';im.save(src,quality=95,exif=ex.tobytes())
fp=digest_image(graffiti.read_image(src))
try:
    lock.write_text(json.dumps(json.loads(orig)+[dict(image_sha256=fp,description='Test')]))
    for vals in ({'exposure':100,'saturation':-100},{}):
        r=render_one(src,OUT/'prot_prev.png',Settings(values=vals,scale=4),preview=True)
        p=r['image'];print('Vorschau',vals,'Datei',Path(p).name,'byte-identisch',filecmp.cmp(p,src,shallow=False),'controls.exposure',r['analysis']['controls']['exposure'],'warn',r['analysis']['warnings'],'backend',r['analysis']['effective_backend'])
    out=OUT/'prot_batch';shutil.rmtree(out,ignore_errors=True);out.with_suffix('.zip').unlink(missing_ok=True)
    res=batch_files([src],out,Settings(export='instagram'))
    with Image.open(next(out.glob('01_prot.jp*'))) as o:print('Stapel-Ergebnisdatei',o.size,'EXIF-Orientierung',o.getexif().get(0x0112))
    slide=Image.open(out/'Instagram'/'01_prot'/'Slide_01.jpg');s=np.array(slide.convert('L'));nz=np.where(s.max(axis=0)>10)[0];rz=np.where(s.max(axis=1)>10)[0]
    print('Instagram-Slide Inhalt (B,H)=',(nz[-1]-nz[0]+1,rz[-1]-rz[0]+1),'; korrekt orientiert waere hochkant',graffiti.read_image(src).size)
    comp=np.array(Image.open(out/'01_Vergleich.jpg').convert('L'))
    for x0,name in ((0,'Original'),(390,'Ergebnis')):
        t=comp[20:,x0:x0+390];cols=np.where((np.abs(t.astype(int)-238)>12).any(axis=0))[0];rows=np.where((np.abs(t.astype(int)-238)>12).any(axis=1))[0]
        print(f'Vergleich {name}-Kachel (B,H)=',(cols[-1]-cols[0]+1,rows[-1]-rows[0]+1))
    print('Beschriftung im Code: "Mit Reglern bearbeitet"')
finally:
    lock.write_text(orig)
