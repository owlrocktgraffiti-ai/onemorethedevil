"""Hinweis 3: Abhängigkeit des Pixel-Fingerabdrucks von Decoder/Version und EXIF; Dateiname-Fallback."""
from common import *
import hashlib,io,sys,json,cv2,PIL
from PIL import ImageOps
import analysis,graffiti
src=OUT/'e2_12mp.jpg'
im=graffiti.read_image(src);h_pil=analysis.digest_image(im)
bgr=cv2.imread(str(src),cv2.IMREAD_COLOR);h_cv=hashlib.sha256(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB).tobytes()).hexdigest()
print('Pillow',PIL.__version__,h_pil[:16]);print('OpenCV',cv2.__version__,h_cv[:16]);print('gleich:',h_pil==h_cv)
# Progressive JPEG
p2=OUT/'e3_prog.jpg';Image.open(src).save(p2,quality=85,progressive=True)
im2=graffiti.read_image(p2);b2=cv2.cvtColor(cv2.imread(str(p2)),cv2.COLOR_BGR2RGB)
print('progressiv gleich:',analysis.digest_image(im2)==hashlib.sha256(b2.tobytes()).hexdigest())
print('max. Pixelabweichung PIL/OpenCV:',int(np.abs(np.array(im).astype(int)-cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB).astype(int)).max()))
# EXIF-Orientierung: gleiches Pixelbild, nur Orientierungs-Tag geändert -> anderer Fingerabdruck
small=Image.open(src).resize((400,300));ex=small.getexif();ex[0x0112]=6
p3=OUT/'e3_exif6.jpg';small.save(p3,quality=90,exif=ex.tobytes());p4=OUT/'e3_exif1.jpg';ex[0x0112]=1;small.save(p4,quality=90,exif=ex.tobytes())
print('EXIF 6 vs 1 gleicher Fingerabdruck:',analysis.digest_image(graffiti.read_image(p3))==analysis.digest_image(graffiti.read_image(p4)))
print('Dateibytes-SHA gleich (JPEG-Nutzdaten identisch bis auf Tag):',hashlib.sha256(open(p3,'rb').read()).hexdigest()==hashlib.sha256(open(p4,'rb').read()).hexdigest())
