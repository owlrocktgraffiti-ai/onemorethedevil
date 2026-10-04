"""Hilfsfunktionen fuer die Reproduktionen von Bereich A (nur Kopien, pkg/ bleibt unveraendert)."""
from pathlib import Path
import shutil, json, subprocess, sys, os, time
BASE = Path('/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad')
PKG_RES = BASE / 'pkg/Graffiti Studio.app/Contents/Resources'
HERE = Path(__file__).resolve().parent
PY = str(BASE / 'venv/bin/python')


def fresh_resources(name):
    """Frische Kopie des Resources-Ordners unter repro/A/work/<name>/Resources."""
    work = HERE / 'work' / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    res = work / 'Resources'
    shutil.copytree(PKG_RES, res, ignore=shutil.ignore_patterns('__pycache__'))
    return work, res


def stub_orientation(res, sleep=0.0, rotate=90):
    """Stub fuer engine/orientation: liefert eine sichere Texterkennung mit Drehung."""
    scores = [dict(rotate=rotate, score=30, characters=20), dict(rotate=0, score=5, characters=3)]
    p = res / 'engine/orientation'
    p.write_text('#!/bin/sh\nsleep %s\necho \'%s\'\n' % (sleep, json.dumps(scores)))
    p.chmod(0o755)
    return p


def bridge(res, command, request, workdir, timeout=300, sigterm_after=None):
    """Startet native_bridge.py wie die Swift-App (stdout=Pipe, stderr=Datei)."""
    req = Path(workdir) / f'{command}_{time.time_ns()}.json'
    req.write_text(json.dumps(request))
    errpath = req.with_suffix('.log')
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    t0 = time.monotonic()
    with open(errpath, 'w') as err:
        proc = subprocess.Popen([PY, str(res / 'native_bridge.py'), command, '--request', str(req)],
                                stdout=subprocess.PIPE, stderr=err, env=env)
        term_at = None
        if sigterm_after is not None:
            time.sleep(sigterm_after)
            proc.terminate(); term_at = time.monotonic() - t0
        out, _ = proc.communicate(timeout=timeout)
    t1 = time.monotonic() - t0
    events = []
    for line in out.decode().splitlines():
        try:
            events.append(json.loads(line))
        except ValueError:
            events.append({'type': '<kein JSON>', 'raw': line})
    return dict(returncode=proc.returncode, events=events, stderr=errpath.read_text(),
                seconds=round(t1, 2), sigterm_at=None if term_at is None else round(term_at, 2))
