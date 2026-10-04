# F8: stdout in Nicht-UTF-8-Kodierung (simuliert ueber PYTHONIOENCODING=latin-1, wie bei LC_CTYPE=ISO8859-1); Swift JSONSerialization verlangt gueltiges UTF-8
from common import *
import shutil
d=V/'work'/'Wände_Köln';d.mkdir(parents=True,exist_ok=True);shutil.copy(V/'test.jpg',d/'Gleis_Ä.jpg')
for label,extra in (('Standard',{}),('latin-1',{'PYTHONIOENCODING':'latin-1'})):
    out=V/'work'/'v8'/label/'Foto'/'Gleis.png'
    rc,ev,raw,err,dt=bridge('export',dict(source=str(d/'Gleis_Ä.jpg'),output=str(out),settings={}),extra)
    bad=0;types=[]
    for line in raw:
        if not line:continue
        try:types.append(json.loads(line.decode('utf-8'))['type'])
        except Exception:bad+=1;types.append('<verworfen>')
    print(f'{label}: rc={rc} Ereignisse={types} | ungueltige UTF-8-Zeilen={bad} | ZIP vorhanden={out.parent.with_suffix(".zip").exists()}')
