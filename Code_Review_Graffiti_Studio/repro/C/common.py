"""Hilfsfunktionen Bereich C (Export). pkg/ bleibt unveraendert; alles laeuft in Kopien unter repro/C/work/<name>."""
from pathlib import Path
import shutil, json, subprocess, os, time, signal, hashlib, sys
BASE = Path('/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad')
PKG_RES = BASE / 'pkg/Graffiti Studio.app/Contents/Resources'
HERE = Path(__file__).resolve().parent
PY = str(BASE / 'venv/bin/python')

def fresh(name):
    work = HERE / 'work' / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    res = work / 'Resources'
    shutil.copytree(PKG_RES, res, ignore=shutil.ignore_patterns('__pycache__'))
    return work, res

def knob(**kw):
    """KnobState.json wie GraffitiStudio.swift:32-35 ihn baut."""
    d = dict(values={}, profile='auto', mode='auto', scale=0, geometry='auto', rotation=None, references=True,
             export='fotos', corners=None, regions=[], strokes=[])
    d.update(kw)
    return d

def knob_json(k):
    r = dict(values=k['values'], profile=k['profile'], mode=k['mode'], scale=k['scale'], geometry=k['geometry'],
             use_saved_retouches=k['references'], export=k['export'], glare_regions=k['regions'], retouch_strokes=k['strokes'])
    if k['rotation'] is not None: r['rotation'] = k['rotation']
    if k['corners'] is not None: r['corners'] = k['corners']
    return r

def swift_export_library(photos, selected, knobs, perPhoto, output):
    """Exakte Nachbildung von StudioModel.exportLibrary (GraffitiStudio.swift:147-150)."""
    perPhoto = {p: dict(v) for p, v in perPhoto.items()}
    if selected is not None: perPhoto[selected] = dict(knobs)
    base = dict(knobs); base.update(corners=None, regions=[], strokes=[], rotation=None)
    specific = {}
    for path, saved in perPhoto.items():
        merged = dict(base); merged['values'] = dict(base['values']); merged['values'].update(saved['values'])
        merged['corners'] = saved['corners']; merged['regions'] = saved['regions']; merged['strokes'] = saved['strokes']; merged['rotation'] = saved['rotation']
        if saved['profile'] != 'auto': merged['profile'] = saved['profile']
        if saved['mode'] != 'auto': merged['mode'] = saved['mode']
        if saved['scale'] != 0: merged['scale'] = saved['scale']
        if not saved['references']: merged['references'] = False
        specific[path] = knob_json(merged)
    return dict(files=list(photos), output=str(output), settings=knob_json(base), per_photo=specific)

def bridge(res, command, request, workdir, timeout=900, on_line=None, env_extra=None):
    """Startet native_bridge.py wie StudioModel.run (stdout Pipe, stderr Datei, PYTHONDONTWRITEBYTECODE=1).
    on_line(proc, event, t) darf z.B. SIGTERM senden."""
    req = Path(workdir) / f'{command}_{time.time_ns()}.json'
    req.write_text(json.dumps(request, ensure_ascii=False), encoding='utf-8')
    errpath = req.with_suffix('.log')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1'); env.update(env_extra or {})
    t0 = time.monotonic(); events = []
    with open(errpath, 'w') as err:
        proc = subprocess.Popen([PY, str(res / 'native_bridge.py'), command, '--request', str(req)], stdout=subprocess.PIPE, stderr=err, env=env)
        for raw in proc.stdout:
            try: ev = json.loads(raw)
            except ValueError: ev = {'type': '<kein JSON>', 'raw': raw.decode(errors='replace')}
            ev['_t'] = round(time.monotonic() - t0, 2); events.append(ev)
            if on_line: on_line(proc, ev, time.monotonic() - t0)
        proc.wait(timeout=timeout)
    return dict(returncode=proc.returncode, events=events, stderr=errpath.read_text(), seconds=round(time.monotonic() - t0, 2))

def final(r):
    return next((e for e in reversed(r['events']) if e.get('type') in ('result', 'error', 'cancelled')), None)

def tree(folder):
    folder = Path(folder)
    return sorted(str(p.relative_to(folder)) for p in folder.rglob('*')) if folder.exists() else None
