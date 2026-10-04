# F6: abgebrochener Einzel-Export hinterlaesst leeren Ordner
import sys,threading,shutil
from pathlib import Path
V=Path(__file__).resolve().parent;sys.path.insert(0,str(V/'Resources'))
from studio_backend import render_one
from adjustments import Settings
folder=V/'work'/'v6'/'Foto_20261004_120000_000'
if folder.parent.exists():shutil.rmtree(folder.parent)
ev=threading.Event();ev.set()
try:render_one(V/'test.jpg',folder/'test.png',Settings(),False,ev,None)
except InterruptedError as e:print('InterruptedError:',e)
print('Ordner existiert:',folder.exists(),'Inhalt:',list(folder.iterdir()))
