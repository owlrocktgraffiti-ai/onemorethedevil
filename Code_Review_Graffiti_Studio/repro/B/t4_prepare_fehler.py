"""Hinweis 4: Fehler im 'prepare'-Befehl (Maskenbild fuer den Editor).
Startet native_bridge.py wie Swift (eigener Prozess, stdout=JSON-Zeilen, stderr=Logdatei) und zeigt,
was Swift sieht: Ereignisse auf stdout, Exitcode, und den Text, den StudioModel.fail() anzeigen wuerde
(String(errors.suffix(2000)) in einer Label-Zeile mit lineLimit(2))."""
import sys, json, pathlib, subprocess, tempfile
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / 'Resources'
PY = sys.executable
from PIL import Image, ImageDraw

work = HERE / 'out_t4'; work.mkdir(exist_ok=True)
src = work / 'quelle.jpg'
img = Image.new('RGB', (4000, 3000), (180, 170, 160)); ImageDraw.Draw(img).rectangle((100, 100, 900, 700), fill=(255, 0, 0)); img.save(src, quality=92)

def call(cmd, settings):
    req = work / 'req.json'
    req.write_text(json.dumps(dict(source=str(src), output=str(work / 'maske.png'), settings=settings)))
    with tempfile.TemporaryFile('w+') as err:
        r = subprocess.run([PY, str(RES / 'native_bridge.py'), cmd, '--request', str(req)], stdout=subprocess.PIPE, stderr=err, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
        err.seek(0); errors = err.read()
    events = [json.loads(l) for l in r.stdout.splitlines() if l.strip()]
    final = [e for e in events if e.get('type') in ('result', 'error', 'cancelled')]
    if final:
        shown = final[-1].get('message') or final[-1]['type']
    else:
        shown = (errors[-2000:] if errors else 'Bildverarbeitung ohne Ergebnis beendet')
    first2 = '\n'.join(shown.splitlines()[:2])
    return r.returncode, events, first2

base = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', use_saved_retouches=False, export='fotos', glare_regions=[], retouch_strokes=[])
cases = {
    'gekreuzte Ecken (Ecke 1 hinter Ecke 2 gezogen)': dict(base, corners=[[0.6, 0], [0.4, 0], [1, 1], [0, 1]]),
    'schmaler Ausschnitt: 3 % Breite (=120 px Vollbild, 54 px nach thumbnail 1800 -> ok?)': dict(base, corners=[[0.5, 0], [0.53, 0], [0.53, 1], [0.5, 1]]),
    'schmaler Ausschnitt: 2.5 % Breite (=100 px Vollbild, 45 px im 1800er Vorschaubild)': dict(base, corners=[[0.5, 0], [0.525, 0], [0.525, 1], [0.5, 1]]),
}
for name, s in cases.items():
    code, events, first2 = call('prepare', s)
    print('==', name)
    print('   Exitcode', code, '| JSON-Ereignisse:', [e['type'] for e in events])
    print('   Swift-Warnzeile (erste 2 Zeilen):', repr(first2))
# Gegenprobe: derselbe 100-px-Ausschnitt im Export (Vollaufloesung) funktioniert
from importlib import import_module
sys.path.insert(0, str(RES))
from photo_prepare import transform
from graffiti import read_image
full = read_image(src)
out = transform(full, dict(corners=cases['schmaler Ausschnitt: 2.5 % Breite (=100 px Vollbild, 45 px im 1800er Vorschaubild)']['corners'], rotate=0))
print('Export-transform desselben Ausschnitts auf Vollaufloesung:', out.size)
