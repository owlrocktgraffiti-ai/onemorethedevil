"""C4: Abbruch im Ordnerexport – Teilergebnisse ohne Protokoll.csv, Pruefbericht.html, ZIP; Swift setzt lastOutput nicht.
SIGTERM wie BridgeJob.cancel (process.terminate) sobald das 3. Foto beginnt."""
from common import *
from PIL import Image
import numpy as np
work, res = fresh('c4')
rng = np.random.default_rng(4)
src = work / 'Eingabe'; src.mkdir()
files = []
for i in range(5):
    p = src / f'foto{i}.png'; Image.fromarray(rng.integers(0, 255, (60, 80, 3), dtype=np.uint8)).resize((1600, 1200)).save(p); files.append(str(p))
out = work / 'Ordner_abbruch'
sent = []
def on_line(proc, ev, t):
    if not sent and ev.get('type') == 'log' and ev.get('message', '').startswith('[3/'):
        proc.send_signal(signal.SIGTERM); sent.append(round(t, 2))
r = bridge(res, 'batch', swift_export_library(files, files[0], knob(mode='klassisch', scale=1), {}, out), work, on_line=on_line)
print('SIGTERM bei t=', sent, 's; Exitcode', r['returncode'], '; letztes Ereignis', {k: v for k, v in final(r).items()})
print('Ordnerinhalt:', tree(out))
print('ZIP vorhanden:', out.with_suffix('.zip').exists(), '| Protokoll.csv:', (out / 'Protokoll.csv').exists(), '| Pruefbericht.html:', (out / 'Pruefbericht.html').exists())
