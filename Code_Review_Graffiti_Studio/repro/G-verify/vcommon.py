"""Gemeinsame Hilfen fuer die Gegenpruefung G-verify. Arbeitet nur auf Kopien."""
import os, sys, json, shutil, subprocess, hashlib, time
from pathlib import Path
import numpy as np
from PIL import Image

BASE = Path('/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad')
HERE = BASE / 'repro/G-verify'
PKG_RES = BASE / 'pkg/Graffiti Studio.app/Contents/Resources'
PY = str(BASE / 'venv/bin/python')
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
sys.dont_write_bytecode = True


def fresh_resources(name):
    dst = HERE / 'runs' / name / 'Resources'
    if dst.parent.exists():
        shutil.rmtree(dst.parent)
    dst.parent.mkdir(parents=True)
    shutil.copytree(PKG_RES, dst, ignore=shutil.ignore_patterns('__pycache__'))
    return dst


def fingerprint(path):
    from PIL import ImageOps
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert('RGB')
    return hashlib.sha256(im.tobytes()).hexdigest()


def make_print_on_table(path, size=(900, 1200)):
    """Hochkant-Foto eines Abzugs (blau) auf braunem Tisch, rechts ein Nachbarabzug (gruen)."""
    w, h = size
    a = np.zeros((h, w, 3), np.uint8)
    a[:] = (140, 90, 45)  # Tisch braun
    # Nachbarabzug rechts
    a[int(.05*h):int(.9*h), int(.88*w):, :] = (40, 170, 60)
    # Hauptabzug (Rechteck innerhalb der Rezeptecken 0.05..0.85 x 0.05..0.93)
    x0, x1, y0, y1 = int(.05*w), int(.85*w), int(.05*h), int(.93*h)
    a[y0:y1, x0:x1] = (240, 240, 240)
    a[y0+15:y1-15, x0+15:x1-15] = (40, 60, 200)
    rng = np.random.default_rng(1)
    a = np.clip(a.astype(int) + rng.integers(-3, 4, a.shape), 0, 255).astype(np.uint8)
    Image.fromarray(a).save(path)
    return [[.05, .05], [.85, .05], [.85, .93], [.05, .93]]


def table_fraction(img):
    a = np.array(img.convert('RGB')).astype(int)
    brown = (abs(a[..., 0]-140) < 30) & (abs(a[..., 1]-90) < 30) & (abs(a[..., 2]-45) < 30)
    green = (abs(a[..., 0]-40) < 35) & (a[..., 1] > 120) & (a[..., 2] < 110)
    return round(float(brown.mean()), 3), round(float(green.mean()), 3)


def bridge(res, command, request, timeout=300, env_extra=None):
    req = res.parent / f'{command}_{time.time_ns()}.json'
    req.write_text(json.dumps(request))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    if env_extra:
        env.update(env_extra)
    r = subprocess.run([PY, str(res / 'native_bridge.py'), command, '--request', str(req)],
                       capture_output=True, text=True, timeout=timeout, env=env)
    events = [json.loads(l) for l in r.stdout.splitlines() if l.strip().startswith('{')]
    return r.returncode, events, r.stderr[-1500:]
