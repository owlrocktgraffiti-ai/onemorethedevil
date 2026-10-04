"""Nach 'Übernehmen' mit gekreuzten Ecken: Vorschau-Prozess wie Swift starten; was kommt auf stdout, was zeigt Swift?"""
import sys, json, pathlib, subprocess
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / 'Resources'
from PIL import Image
work = HERE / 'out_t8'; work.mkdir(exist_ok=True)
src = work / 'q.jpg'; Image.new('RGB', (800, 600), (100, 100, 100)).save(src)
s = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', use_saved_retouches=False, export='fotos', glare_regions=[], retouch_strokes=[], corners=[[0.6, 0], [0.4, 0], [1, 1], [0, 1]])
(work / 'req.json').write_text(json.dumps(dict(source=str(src), output=str(work / 'p.png'), settings=s)))
log = work / 'stderr.log'
with log.open('w') as err:
    r = subprocess.run([sys.executable, str(RES / 'native_bridge.py'), 'preview', '--request', str(work / 'req.json')], stdout=subprocess.PIPE, stderr=err, text=True, env={'PYTHONDONTWRITEBYTECODE': '1', 'PATH': '/usr/bin:/bin'})
errors = log.read_text()
print('Exitcode', r.returncode, '| stdout:', repr(r.stdout))
print('Swift warning (lineLimit 2):', repr('\n'.join(errors[-2000:].splitlines()[:2])))
print('letzte stderr-Zeile (nicht sichtbar):', errors.strip().splitlines()[-1])
