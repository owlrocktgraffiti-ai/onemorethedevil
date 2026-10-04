"""Hilfsfunktionen fuer Bereich G. Arbeitet NUR auf Kopien unter repro/G."""
import json, os, shutil, subprocess, sys
from pathlib import Path
BASE = Path('/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad')
PKG_RES = BASE / 'pkg/Graffiti Studio.app/Contents/Resources'
G = BASE / 'repro/G'
PY = str(BASE / 'venv/bin/python')

def fresh_resources(name):
    dst = G / 'work' / name / 'Resources'
    if dst.parent.exists(): shutil.rmtree(dst.parent)
    shutil.copytree(PKG_RES, dst, ignore=shutil.ignore_patterns('__pycache__'))
    return dst

def bridge(res, command, request, workdir, timeout=300, env_extra=None):
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    req = workdir / f'{command}_request.json'; req.write_text(json.dumps(request))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', **(env_extra or {}))
    r = subprocess.run([PY, str(res / 'native_bridge.py'), command, '--request', str(req)], capture_output=True, text=True, timeout=timeout, env=env)
    events = []
    for line in r.stdout.splitlines():
        try: events.append(json.loads(line))
        except ValueError: events.append({'type': 'NICHT-JSON', 'raw': line})
    return r.returncode, events, r.stderr

def py_in(res, code, timeout=300):
    """Python-Code mit Resources-Kopie im Pfad in eigenem Prozess ausfuehren."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    r = subprocess.run([PY, '-c', f'import sys;sys.path.insert(0,{str(res)!r});' + code], capture_output=True, text=True, timeout=timeout, env=env)
    return r.returncode, r.stdout, r.stderr
