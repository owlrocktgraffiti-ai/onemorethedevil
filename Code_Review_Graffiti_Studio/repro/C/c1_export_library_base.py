"""C1/C3: exportLibrary (GraffitiStudio.swift:147-150) – geometry/use_saved_retouches/Reglerwerte des GERADE
gewaehlten Fotos gelten fuer alle Fotos. Request exakt wie Swift (common.swift_export_library), Ausfuehrung mit
native_bridge.py batch. Foto A = Abzug mit hinterlegtem Fotorezept (wie IMG_4363: Ecken + rotate 90),
Foto B = Foto mit bekannter Referenzretusche (wie WFTPXN), Foto C = beliebiges aktuelles Foto."""
from common import *
from PIL import Image
import numpy as np
work, res = fresh('c1')
sys.path.insert(0, str(res))
from analysis import digest_image
from graffiti import read_image
rng = np.random.default_rng(1)
W, H = 900, 1200
img = np.zeros((H, W, 3), np.uint8); img[:] = (150, 100, 60)          # "Tisch"
img[60:H-84, 45:W-135] = np.array(Image.fromarray(rng.integers(0, 255, (60, 45, 3), dtype=np.uint8)).resize((W-180, H-144), Image.BICUBIC))
A = work / 'Abzug.png'; Image.fromarray(img).save(A)
rec = json.loads((res / 'Fotorezepte.json').read_text())
rec['Abzug.png'] = dict(corners=[[0.05, 0.05], [0.85, 0.05], [0.85, 0.93], [0.05, 0.93]], rotate=90, glare_strength=0.62, source_size=[W, H], image_sha256=digest_image(read_image(A)))
(res / 'Fotorezepte.json').write_text(json.dumps(rec, indent=2))
Bp = work / 'Wand.png'; Image.fromarray(rng.integers(0, 255, (300, 400, 3), dtype=np.uint8)).save(Bp)
(res / 'Referenzkorrekturen').mkdir(exist_ok=True)
cached = res / 'Referenzkorrekturen/Test.png'; Image.new('RGB', (400, 300), (0, 200, 0)).save(cached)
known = json.loads((res / 'Bekannte_Retuschen.json').read_text())
known.append(dict(source_name='Wand.png', image_sha256=digest_image(read_image(Bp)), cached='Referenzkorrekturen/Test.png', cached_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(), description='Test', generative_reconstruction=True))
(res / 'Bekannte_Retuschen.json').write_text(json.dumps(known, indent=2))
Cp = work / 'Zug.png'; Image.fromarray(rng.integers(60, 200, (500, 700, 3), dtype=np.uint8)).save(Cp)
files = [str(A), str(Bp), str(Cp)]

def run(tag, current_knobs, perPhoto):
    out = work / ('Ordner_' + str(time.time_ns()))
    req = swift_export_library(files, str(Cp), current_knobs, perPhoto, out)
    f = final(bridge(res, 'batch', req, work))
    assert f['type'] == 'result', f
    pa = json.loads((out / '01_Abzug.json').read_text()); pb = json.loads((out / '02_Wand.json').read_text())
    with Image.open(out / '01_Abzug.png') as im: sa = im.size
    with Image.open(out / '02_Wand.png') as im: g = np.array(im.convert('RGB')).reshape(-1, 3).mean(0).round()
    print(f'{tag:58s} | Abzug {sa} {"gedreht+zugeschnitten" if sa[0] > sa[1] else "UNGESCHNITTEN/HOCHKANT samt Tisch"} glare={pa["controls"]["glare"]:3d} contrast={pa["controls"]["contrast"]:4d} profil={pa["settings"]["profile"]}'
          f' | Wand: Referenz {"angewendet" if g[1] > 150 and g[0] < 60 else "NICHT angewendet"} | gesendet A: geometry={req["per_photo"].get(str(A), req["settings"])["geometry"]} refs B={req["per_photo"].get(str(Bp), req["settings"])["use_saved_retouches"]}')

# 1) Referenzfall: aktuelles Foto C unveraendert (alles Auto)
run('1 aktuelles Foto C: Automatik', knob(mode='klassisch', scale=1), {})
# 2) Auf C "Automatische Papierkanten" aus (z.B. weil C kein Abzug ist) -> gilt fuer ALLE
run('2 auf C Papierkanten AUS', knob(mode='klassisch', scale=1, geometry='aus'), {})
# 3) A wurde besucht (alles Auto, geometry auto), C hat Papierkanten aus -> A trotzdem aus
run('3 A besucht (auto), auf C Papierkanten AUS', knob(mode='klassisch', scale=1, geometry='aus'), {str(A): knob(mode='klassisch', scale=1)})
# 4) Auf C Ecken-Editor geoeffnet und "Uebernehmen" (openMask: Vollbild-Ecken; closeMask: references=false)
run('4 auf C Masken-Editor uebernommen', knob(mode='klassisch', scale=1, corners=[[0, 0], [1, 0], [1, 1], [0, 1]], references=False), {})
# 5) Umgekehrt: Nutzer hat bei A die Papierkanten bewusst AUS, aktuelles C auto -> A wird trotzdem zugeschnitten
run('5 A: Papierkanten AUS gewaehlt, C auto', knob(mode='klassisch', scale=1), {str(A): knob(mode='klassisch', scale=1, geometry='aus')})
# 6) C3: A besucht, Regler auf Auto; aktuelles C hat explizit Kontrast -100, Reflex 0, Profil nacht
run('6 A besucht (Auto); C: contrast=-100 glare=0 profil=nacht', knob(mode='klassisch', scale=1, profile='nacht', values=dict(contrast=-100, glare=0)), {str(A): knob(mode='klassisch', scale=1)})
