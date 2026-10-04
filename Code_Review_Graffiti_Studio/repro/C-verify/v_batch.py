"""Gegenpruefung C2, C3, C4, C5, C13, C14, C17 ueber native_bridge bzw. studio_backend (Kopie der Resources)."""
import sys, json, os, subprocess, shutil, threading, zipfile, csv
from pathlib import Path
HERE = Path(__file__).resolve().parent
RES = HERE / 'Resources'; PY = sys.executable
sys.path.insert(0, str(RES))
import numpy as np
from PIL import Image
W = HERE / 'work_batch'; shutil.rmtree(W, ignore_errors=True); W.mkdir()

def mkimg(p, w=1000, h=800, seed=0, exif=None):
    rng = np.random.default_rng(seed)
    a = rng.integers(40, 200, (h // 8, w // 8, 3)).astype(np.uint8)
    im = Image.fromarray(a).resize((w, h), Image.Resampling.NEAREST)
    p.parent.mkdir(parents=True, exist_ok=True)
    if exif is not None: im.save(p, exif=exif, quality=92)
    else: im.save(p, quality=92)
    return p

def bridge(cmd, req):
    rp = W / f'req_{cmd}_{len(list(W.glob("req_*")))}.json'; rp.write_text(json.dumps(req))
    r = subprocess.run([PY, str(RES / 'native_bridge.py'), cmd, '--request', str(rp)], capture_output=True, text=True, timeout=900)
    ev = [json.loads(l) for l in r.stdout.splitlines() if l.strip().startswith('{')]
    return r.returncode, ev, r.stderr[-300:]

sel = sys.argv[1:] or ['c2', 'c3', 'c4', 'c5', 'c13', 'c14']
BASE = dict(values={}, profile='auto', mode='klassisch', scale=1, geometry='auto', use_saved_retouches=True, export='fotos', glare_regions=[], retouch_strokes=[])

if 'c2' in sel:
    print('--- C2 Symlink ---')
    real = W / 'real'; mkimg(real / 'foto.jpg'); link = W / 'link'; link.symlink_to(real, target_is_directory=True)
    spec = dict(BASE, corners=[[0, 0], [.5, 0], [.5, .5], [0, .5]], rotation=90)
    for label, folder in [('Symlink-Pfad', link), ('realer Pfad', real)]:
        f = str(folder / 'foto.jpg')
        code, ev, err = bridge('batch', dict(files=[f], output=str(W / f'out_c2_{label[:4]}'), settings=BASE, per_photo={f: spec}))
        res = ev[-1]; out = Path(res['result']['folder']) if res['type'] == 'result' else None
        plan = json.loads((out / '01_foto.json').read_text())
        with Image.open(out / '01_foto.png') as im: size = im.size
        print(f'{label}: Ende={res["type"]} Bild={size} settings.corners={plan["settings"]["corners"]} warnings={res["result"]["warnings"]}')

if 'c3' in sel:
    print('--- C3 ungueltiger per_photo-Eintrag fremder Datei ---')
    a = mkimg(W / 'c3' / 'a.jpg', seed=3)
    bad = dict(BASE, corners=[[0, 0], [1, 1], [1, 0], [0, 1]])
    code, ev, err = bridge('batch', dict(files=[str(a)], output=str(W / 'out_c3'), settings=BASE, per_photo={'/Alter_Ordner/IMG_0001.jpg': bad}))
    print('gekreuzte Ecken (fremdes Foto):', ev[-1], '| Ausgabeordner existiert:', (W / 'out_c3').exists())
    code, ev, err = bridge('batch', dict(files=[str(a)], output=str(W / 'out_c3b'), settings=BASE, per_photo={'/Alter_Ordner/IMG_0001.jpg': dict(BASE, values={'contrast': 15})}))
    print('contrast=15 (fremdes Foto):', ev[-1])
    code, ev, err = bridge('preview', dict(source=str(a), output=str(W / 'pv.png'), settings=bad))
    print('Vorschau mit gekreuzten Ecken: Exitcode', code, 'Ereignisse', ev, 'stderr-Ende:', err.strip().splitlines()[-1])

if 'c4' in sel:
    print('--- C4 Abbruch ---')
    from adjustments import Settings
    from studio_backend import batch_files
    files = [mkimg(W / 'c4' / f'f{i}.jpg', seed=10 + i) for i in range(4)]
    cancel = threading.Event()
    def prog(stage, frac):
        if stage.startswith('3/'): cancel.set()
    out = W / 'out_c4'
    try: batch_files(files, out, Settings(mode='klassisch', scale=1), cancel, prog); print('kein Abbruch?!')
    except InterruptedError as e: print('InterruptedError:', e)
    print('Inhalt:', sorted(p.name for p in out.iterdir()), '| ZIP:', out.with_suffix('.zip').exists())

if 'c5' in sel:
    print('--- C5 Fehler beim ZIP ---')
    from adjustments import Settings
    import studio_backend
    files = [mkimg(W / 'c5' / f'f{i}.jpg', seed=20 + i) for i in range(3)]
    orig = zipfile.ZipFile.write; n = {'k': 0}
    def bad_write(self, *a, **k):
        n['k'] += 1
        if n['k'] == 4: raise OSError(28, 'No space left on device')
        return orig(self, *a, **k)
    zipfile.ZipFile.write = bad_write
    out = W / 'out_c5'
    try: studio_backend.batch_files(files, out, Settings(mode='klassisch', scale=1)); print('kein Fehler?!')
    except Exception as e: print('Ausnahme an Bruecke ->', type(e).__name__, e)
    finally: zipfile.ZipFile.write = orig
    z = out.with_suffix('.zip'); print('Ordner:', sorted(p.name for p in out.iterdir()))
    print('ZIP unter Endnamen:', z.exists(), z.stat().st_size if z.exists() else '-')
    try:
        with zipfile.ZipFile(z) as zz: print('ZIP lesbar, Eintraege', len(zz.namelist()), 'von', sum(1 for p in out.rglob('*') if p.is_file()))
    except Exception as e: print('ZIP defekt:', e)

if 'c13' in sel:
    print('--- C13 lange Namen ---')
    for stem_len in (236, 237, 239, 240):
        stem = 'a' * stem_len; p = mkimg(W / 'c13' / f'{stem}.jpg', 300, 200, seed=stem_len)
        code, ev, err = bridge('batch', dict(files=[str(p)], output=str(W / f'out_c13_{stem_len}'), settings=BASE, per_photo={}))
        rows = list(csv.reader((W / f'out_c13_{stem_len}' / 'Protokoll.csv').open(encoding='utf-8-sig')))
        e2 = bridge('export', dict(source=str(p), output=str(W / f'out_c13e_{stem_len}' / f'{stem}.png'), settings=BASE))[1][-1]
        print(f'Stamm {stem_len} Byte: Ordner -> {ev[-1]["type"]} {rows[1][2]} {rows[1][3][:40]} | Einzel -> {e2["type"]} {e2.get("message", "")[:40]}')

if 'c14' in sel or 'c17' in sel:
    print('--- C14/C17 Pfade und EXIF ---')
    ex = Image.Exif(); ex[0x0110] = 'Testkamera'; ex.get_ifd(0x8769)[0x9003] = '2019:07:01 18:20:34'
    p = mkimg(W / 'c14' / 'wand.jpg', seed=7, exif=ex)
    code, ev, err = bridge('batch', dict(files=[str(p)], output=str(W / 'out_c14'), settings=dict(BASE, export='instagram'), per_photo={}))
    res = ev[-1]['result']; z = zipfile.ZipFile(res['zip'])
    hits = [n for n in z.namelist() if str(W).encode() in z.read(n)]
    print('ZIP-Eintraege mit absolutem Pfad:', hits)
    print('CSV-Zeile:', (W / 'out_c14' / 'Protokoll.csv').read_text(encoding='utf-8-sig').splitlines()[1])
    with Image.open(p) as im: print('Quelle EXIF DateTimeOriginal:', im.getexif().get_ifd(0x8769).get(0x9003))
    with Image.open(W / 'out_c14' / '01_wand.png') as im: print('Export-PNG EXIF:', dict(im.getexif()) or 'keine')
    sl = next((W / 'out_c14' / 'Instagram').rglob('Slide_01.jpg'))
    with Image.open(sl) as im: print('Slide EXIF:', dict(im.getexif()) or 'keine')
