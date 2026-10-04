"""A1: Fensterschliessen = App beenden (applicationShouldTerminateAfterLastWindowClosed=true); applicationWillTerminate
ruft shutdown() -> job.cancel() -> SIGTERM an den laufenden Ordnerexport, ohne Rueckfrage. Hier: Batch mit 4 Fotos,
SIGTERM nach ~4 s (wie beim Schliessen). Ergebnis: halbfertiger Ordner ohne Protokoll/Pruefbericht/ZIP.
"""
from common import *
from PIL import Image
import numpy as np
work, res = fresh_resources('r11')
rng = np.random.default_rng(11); files = []
for i in range(4):
    p = work / f'IMG_{i}.jpg'; Image.fromarray(rng.integers(0, 255, (189, 252, 3), dtype=np.uint8)).resize((4032, 3024)).save(p, quality=90); files.append(str(p))
out = work / 'Ordner_20261004_120000_000'
r = bridge(res, 'batch', dict(files=files, output=str(out), settings=dict(mode='klassisch')), work, sigterm_after=4.0)
print('SIGTERM nach', r['sigterm_at'], 's; letzte Ereignisart:', r['events'][-1]['type'])
print('Inhalt des Ergebnisordners:', sorted(x.name for x in out.iterdir()))
print('ZIP vorhanden:', out.with_suffix('.zip').exists())
