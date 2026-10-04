# F5: vendor/ mit cp314-Erweiterung verdeckt das laufzeiteigene numpy; Import scheitert vor dem try
from common import *
import shutil,importlib.machinery
res=V/'work'/'Res_vendor'
if res.exists():shutil.rmtree(res)
shutil.copytree(RES,res)
np_dir=res/'vendor'/'numpy';np_dir.mkdir(parents=True)
(np_dir/'__init__.py').write_text('from . import _multiarray_umath\n')
(np_dir/'_multiarray_umath.cpython-314-darwin.so').write_bytes(b'\0')
print('Endungen dieser Laufzeit:',importlib.machinery.EXTENSION_SUFFIXES)
rc,ev,_,err,dt=bridge('preview',dict(source=str(V/'test.jpg'),output=str(V/'work'/'v5'/'o.png'),settings={}),res=res)
print(f'rc={rc} JSON-Ereignisse={len(ev)} letzte stderr-Zeile={err.strip().splitlines()[-1]!r}')
print('Swift-Anzeige:',repr(swift_display(err)))
