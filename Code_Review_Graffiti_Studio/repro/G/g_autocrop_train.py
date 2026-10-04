"""Chat_Korrekturen.md:11 'Keine ungepruefte automatische Beschneidung unbekannter Zuege'.
Synthetisches Zugfoto (kein Papierabzug): Wagenkasten als grosses Rechteck vor warmer Backsteinmauer,
Raeder/Dach ausserhalb. Standardeinstellungen der App (geometry=auto). OCR-Laufzeit fehlt hier (wie ohne engine/orientation)."""
import sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
import numpy as np, cv2
from PIL import Image
res = fresh_resources('train'); wd = res.parent
a = np.clip(np.full((1000, 1500, 3), (175, 110, 70), np.int16) + np.random.default_rng(8).integers(-12, 12, (1000, 1500, 1)), 0, 255).astype(np.uint8)  # Backsteinmauer (warm) hinter dem Zug
pass
cv2.rectangle(a, (60, 120), (1440, 820), (150, 30, 30), -1)            # Wagenkasten
rng = np.random.default_rng(5)
for i in range(25):                                                    # Graffiti auf dem Wagen
    x, y = int(rng.integers(100, 1300)), int(rng.integers(160, 700)); cv2.rectangle(a, (x, y), (x + 90, y + 80), tuple(int(c) for c in rng.integers(0, 255, 3)), -1)
for x in (200, 400, 1100, 1300): cv2.circle(a, (x, 875), 40, (20, 20, 20), -1)   # Raeder unterhalb des Wagenkastens
cv2.rectangle(a, (60, 70), (1440, 100), (110, 110, 110), -1)           # Dach
Image.fromarray(a).save(wd / 'zug_seitenansicht.jpg', quality=95)
for label, s in [('Standard (geometry=auto)', {}), ('Automatische Papierkanten aus', dict(geometry='aus'))]:
    code, ev, err = bridge(res, 'preview', dict(source=str(wd / 'zug_seitenansicht.jpg'), output=str(wd / ('p_' + str(len(s)) + '.png')), settings=dict(s, mode='klassisch')), wd)
    plan = ev[-1]['result']['analysis']
    print(f'{label:30} Ausgabe {Image.open(ev[-1]["result"]["image"]).size} von 1500x1000 | paper_confidence={plan.get("paper_confidence")} '
          f'| preparation.corners={(plan.get("preparation") or {}).get("corners")} | executed[0]={plan["executed"][0]!r} | Warnungen={plan["warnings"]}')
