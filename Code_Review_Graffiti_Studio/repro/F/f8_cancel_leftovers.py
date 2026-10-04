"""F8: Rueckstaende nach Abbruch bzw. nach Vorschauen.
 a) Einzelexport, Abbruch (SIGTERM) waehrend 'Speichern' -> was bleibt im Ausgabeordner?
 b) Drei Vorschauen in ein gemeinsames temp-Verzeichnis + Nachbildung von clearOldPreviews (Swift:140)
    -> welche Dateien bleiben liegen?
 c) Fehlermeldungen mit leerem Text (str(e) == '') fuer AssertionError/MemoryError (native_bridge.py:57)
Aufruf: venv/bin/python repro/F/f8_cancel_leftovers.py
"""
import signal, uuid
from common import *

work, res = fresh('f8')
src = noise_photo(work / 'wand.jpg', size=(4000, 3000))

# a)
out = work / 'Graffiti_Studio_Ergebnisse' / 'Foto_20261004_111111_111' / 'wand.png'
b = Bridge(res, 'export', dict(source=str(src), output=str(out), settings=dict(mode='klassisch', scale=1)), work)
def on_event(br, ev):
    if ev.get('stage') == 'Speichern':
        br.proc.send_signal(signal.SIGTERM); br.events.append({'type': '<SIGTERM gesendet>', '_t': br.t()})
b.callbacks.append(on_event)
b.wait()
print('a)', [e['type'] for e in b.events][-2:], '| Ausgabeordner existiert:', out.parent.exists(), '| Inhalt:', sorted(p.name for p in out.parent.iterdir()) if out.parent.exists() else '-',
      '| ZIP:', out.parent.with_suffix('.zip').exists())

# b)
temp = work / 'GraffitiStudio-TEMP'; temp.mkdir()
small = noise_photo(work / 'klein.jpg', size=(1200, 900))
for i in range(3):
    target = temp / f'{uuid.uuid4()}.png'
    r = Bridge(res, 'preview', dict(source=str(small), output=str(target), settings=dict(values=dict(contrast=10 * i))), work).wait()
    keep = r.events[-1]['result']['image']
    # clearOldPreviews(keeping:): loescht nur .png ausser der aktuellen Datei
    for f in temp.iterdir():
        if f.suffix == '.png' and str(f) != keep and f.with_suffix('') != Path(keep).with_suffix(''):
            f.unlink()
left = sorted(temp.iterdir())
print('b) nach 3 Vorschauen im temp-Ordner:', [(p.suffix, p.stat().st_size) for p in left])

# c)
for exc in (AssertionError(), MemoryError()):
    print('c)', type(exc).__name__, '-> message =', repr(str(exc)))
