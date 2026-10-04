"""Zusatz: KI-Modus bei Bildern > 3,5 MP – Modell bekommt verkleinerte Eingabe, Ergebnis wird zu 60 % beigemischt."""
import os,shutil,numpy as np,cv2
from PIL import Image
import common,graffiti
from adjustments import Settings,CONTROL_SPEC
OUT=common.OUT/'t13';OUT.mkdir(exist_ok=True)
engine=common.RES/'engine/realesrgan-ncnn-vulkan';shutil.copy(common.HERE/'stubs/realesrgan_lanczos.py',engine);os.chmod(engine,0o755)
rng=np.random.default_rng(13);W,H=4032,3024
a=np.full((H,W,3),200,np.uint8)
for i in range(400):cv2.putText(a,'tag',(int(rng.integers(0,W-80)),int(rng.integers(20,H))),cv2.FONT_HERSHEY_PLAIN,1.0,(20,20,20),1,cv2.LINE_AA)
src=OUT/'feinschrift.png';Image.fromarray(a).save(src)
zero={k:0 for k in CONTROL_SPEC}
res={}
for mode,ki in (('klassisch',0),('ki',60)):
    v=dict(zero,ki_strength=ki,color_protection=60);graffiti.SESSION['ai_available']=True
    im,plan=graffiti.process(src,OUT/f'{mode}.png',mode,1,'auto','auto',None,Settings(mode=mode,scale=1,values=v))
    g=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2GRAY).astype(float);res[mode]=g
    print(f'{mode:9s}: backend={plan["effective_backend"]} Laplace-Varianz={cv2.Laplacian(g,cv2.CV_64F).var():.0f} Abweichung vom Original: mittel {np.abs(g-cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)).mean():.2f}, max {np.abs(g-cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)).max():.0f}; Hinweise={[n for n in plan["executed"] if "KI" in n]}')
engine.unlink()
