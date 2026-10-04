"""LIES_MICH.txt:20-21 'Die bekannten generativen Referenzen sind im Ergebnisplan gekennzeichnet' /
'Das tatsaechlich eingesetzte Verfahren steht im Plan und Protokoll'. Synthetisches Foto wird in der KOPIE von
Bekannte_Retuschen.json als bekannte KI-Referenz eingetragen (wie WFTPXN...)."""
import sys, json, hashlib, csv
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np
from PIL import Image
res = fresh_resources('generative'); wd = res.parent
rng = np.random.default_rng(7)
Image.fromarray(rng.integers(30, 220, (600, 900, 3), dtype=np.uint8)).save(wd / 'WFTPXN_synthetisch.png')
code, out, err = py_in(res, f'from graffiti import read_image;from analysis import digest_image;from pathlib import Path;print(digest_image(read_image(Path({str(wd / "WFTPXN_synthetisch.png")!r}))))')
fp = out.strip()
(res / 'Referenzkorrekturen').mkdir(exist_ok=True)
Image.new('RGB', (900, 600), (200, 40, 40)).save(res / 'Referenzkorrekturen' / 'Korrektur_01.png')
rec = json.loads((res / 'Bekannte_Retuschen.json').read_text())
rec[0]['image_sha256'] = fp; rec[0]['cached_sha256'] = hashlib.sha256((res / 'Referenzkorrekturen/Korrektur_01.png').read_bytes()).hexdigest()
(res / 'Bekannte_Retuschen.json').write_text(json.dumps(rec, indent=2))
code, ev, err = bridge(res, 'preview', dict(source=str(wd / 'WFTPXN_synthetisch.png'), output=str(wd / 'p.png'), settings={}), wd)
plan = ev[-1]['result']['analysis']
print('Vorschau: effective_backend =', plan['effective_backend'], '-> Swift-Statuszeile (GraffitiStudio.swift:133): "Vorschau fertig · ' + ('Lokale KI' if plan['effective_backend'] == 'lokale_ki' else 'Klassisch') + '"')
print('  executed:', plan['executed'])
print('  warnings[0] (einzige Warnung, die die App anzeigt, Swift:133 warnings.first):', plan['warnings'][0])
code, ev, err = bridge(res, 'batch', dict(files=[str(wd / 'WFTPXN_synthetisch.png')], output=str(wd / 'Ordner'), settings={}), wd)
print('Stapel:', ev[-1]['type'])
with open(wd / 'Ordner' / 'Protokoll.csv', encoding='utf-8-sig') as f:
    for row in csv.reader(f): print('  Protokoll.csv:', row)
