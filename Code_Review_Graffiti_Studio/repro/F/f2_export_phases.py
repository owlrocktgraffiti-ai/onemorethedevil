"""F2: Phasen ohne Checkpoint beim Einzelexport eines grossen Fotos (Speichern, Instagram, ZIP + testzip).
Misst die Abstaende zwischen den Fortschrittsereignissen und sendet SIGTERM, sobald 'Fertig' (1.0) gemeldet wurde
(= Nutzer klickt 'Abbrechen' waehrend die App bereits 100 % zeigt). Erwartung laut LIES_MICH: Abbruch.
Aufruf: venv/bin/python repro/F/f2_export_phases.py
"""
import signal, zipfile
import numpy as np
from PIL import Image
from common import *

work, res = fresh('f2')
rng = np.random.default_rng(2)
base = Image.fromarray(rng.integers(0, 255, (300, 400, 3), dtype=np.uint8)).resize((6000, 4500), Image.BICUBIC)
a = np.asarray(base).astype(np.int16) + rng.normal(0, 4, (4500, 6000, 3)).astype(np.int16)
src = work / 'gross.jpg'
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(src, quality=92)
print('Quelle', src.stat().st_size // 1024, 'KiB, 27 MP')

import threading, time
def run(delay, label):
    out = work / 'Ausgabe' / f'Foto_{label}' / 'gross.png'
    b = Bridge(res, 'export', dict(source=str(src), output=str(out), settings=dict(mode='klassisch', scale=2, export='instagram')), work)
    sent = []
    def on_event(br, ev):
        if delay is not None and ev.get('type') == 'progress' and ev.get('stage') == 'Fertig' and not sent:
            def later():
                time.sleep(delay); br.proc.send_signal(signal.SIGTERM); sent.append(br.t()); br.events.append({'type': '<SIGTERM gesendet>', '_t': br.t()})
            threading.Thread(target=later, daemon=True).start()
    b.callbacks.append(on_event)
    b.wait()
    print('===', label, '(SIGTERM %s s nach Fertig)' % delay)
    print(b.summary())
    return b, out, sent
b, out, sent = run(None, 'ohne_Abbruch')
print('Exitcode', b.returncode, '| Ende nach', b.seconds, 's')
b, out, sent = run(0.3, 'Abbruch_nach_Fertig')
print('Exitcode', b.returncode, '| Ende nach', b.seconds, 's | SIGTERM bei', sent, '| letzte Ereignisart', [e['type'] for e in b.events][-1])
z = out.parent.with_suffix('.zip')
print('PNG', round(out.stat().st_size / 2**20, 1), 'MiB; ZIP vorhanden', z.exists(), round(z.stat().st_size / 2**20, 1) if z.exists() else '', 'MiB')
if sent:
    print('Zeit zwischen SIGTERM und Prozessende (ohne Checkpoint):', round(b.seconds - sent[0], 2), 's')
# Vergleich: ZIP_STORED statt ZIP_DEFLATED fuer dieselben Dateien
import time
for method, name in ((zipfile.ZIP_DEFLATED, 'DEFLATED'), (zipfile.ZIP_STORED, 'STORED')):
    t0 = time.monotonic(); tmp = work / f'vergleich_{name}.zip'
    with zipfile.ZipFile(tmp, 'w', method) as zf:
        for item in out.parent.rglob('*'):
            if item.is_file(): zf.write(item, item.relative_to(out.parent))
    t1 = time.monotonic()
    with zipfile.ZipFile(tmp) as zf: assert zf.testzip() is None
    print(f'{name}: schreiben {t1 - t0:.2f}s, testzip {time.monotonic() - t1:.2f}s, Groesse {tmp.stat().st_size / 2**20:.1f} MiB')
