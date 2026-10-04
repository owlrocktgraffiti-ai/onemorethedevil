"""A1: Ein per SIGTERM abgebrochener Vorschauprozess laeuft weiter, bis der naechste Checkpoint
erreicht ist (hier: OCR-Stub mit 8 s). Solange blockiert er in der Swift-App die SERIELLE worker-Queue,
d. h. ein neuer Export/eine neue Vorschau startet erst danach (BridgeJob.start im naechsten Block).
"""
from common import *
from PIL import Image
import numpy as np

work, res = fresh_resources('r1')
stub_orientation(res, sleep=8)
rng = np.random.default_rng(1)
# Glattes Rauschbild ohne Papierkante -> analyze() ruft orientation(image) auf
small = rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)
img = Image.fromarray(small).resize((1600, 1200), Image.BICUBIC)
src = work / 'wand.jpg'; img.save(src, quality=90)

r = bridge(res, 'preview', dict(source=str(src), output=str(work / 'p.png'), settings={}), work, sigterm_after=2.0)
print('SIGTERM gesendet nach', r['sigterm_at'], 's; Prozessende nach', r['seconds'], 's; Exitcode', r['returncode'])
print('Ereignisse:', [e.get('type') + (':' + e.get('stage', '') if e.get('type') == 'progress' else '') for e in r['events']])
print('stderr:', r['stderr'][-300:] or '<leer>')

# Gegenprobe ohne SIGTERM: Laufzeit einer normalen Vorschau mit 8-s-OCR
r2 = bridge(res, 'preview', dict(source=str(src), output=str(work / 'p2.png'), settings={}), work)
print('Ohne Abbruch: Ende nach', r2['seconds'], 's; letzte Ereignisart', r2['events'][-1]['type'])
