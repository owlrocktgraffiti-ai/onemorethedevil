"""D5 (Hinweis 5): Welche KI-Fehler fängt process() ab? Stub liefert Exit 0 mit fehlerhafter Ausgabe."""
import os,shutil
import numpy as np
from PIL import Image
import common
import graffiti
from adjustments import Settings
OUT=common.OUT/'t5';OUT.mkdir(exist_ok=True)
engine=common.RES/'engine/realesrgan-ncnn-vulkan';shutil.copy(common.HERE/'stubs/realesrgan_badout.py',engine);os.chmod(engine,0o755)
rng=np.random.default_rng(5)
src=OUT/'small.png';Image.fromarray((rng.normal(0,30,(500,700,3))+120).clip(0,255).astype(np.uint8)).save(src)
for kind in ('garbage','truncated','gray16','tiny','black'):
    os.environ['STUB_KIND']=kind;graffiti.SESSION['ai_available']=True
    try:
        im,plan=graffiti.process(src,OUT/f'{kind}.png','ki',2,'auto','auto',None,Settings(mode='ki',scale=2))
        a=np.array(im).astype(float)
        print(f'{kind:10s}: abgefangen={plan["effective_backend"]=="klassisch"} backend={plan["effective_backend"]} Ergebnis-Mittel={a.mean():.1f} (Eingabe ~120) Hinweis={[n[:70] for n in plan["executed"] if "KI" in n or "Real" in n]}')
    except Exception as e:print(f'{kind:10s}: NICHT abgefangen: {type(e).__name__}: {e}')
engine.unlink()
