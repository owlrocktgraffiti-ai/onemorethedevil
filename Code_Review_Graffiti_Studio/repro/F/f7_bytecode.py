"""F7: Startkosten jedes Bridge-Prozesses, wenn vendor/ ohne .pyc ausgeliefert wird (zip_native.py schliesst
__pycache__/.pyc aus) und Swift PYTHONDONTWRITEBYTECODE=1 setzt -> jede Vorschau kompiliert numpy/cv2/PIL neu.
Vergleich: dieselben Pakete mit vorkompilierten .pyc bzw. mit PYTHONPYCACHEPREFIX ausserhalb des Bundles.
Aufruf: venv/bin/python repro/F/f7_bytecode.py
"""
import compileall, os, shutil, statistics, subprocess, time
from common import *

work, res = fresh('f7')
sp = Path(PY).parent.parent / 'lib/python3.12/site-packages'
vendor = res / 'vendor'
for name in ('numpy', 'numpy.libs', 'cv2', 'opencv_python_headless.libs', 'PIL', 'pillow.libs'):
    if (sp / name).exists():
        shutil.copytree(sp / name, vendor / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
src = noise_photo(work / 'klein.jpg', size=(400, 300))
probe = ("import sys,time;t=time.perf_counter();sys.path.insert(0,%r);sys.path.insert(0,%r);"
         "import adjustments,studio_backend,graffiti;import numpy;assert numpy.__file__.startswith(%r);"
         "print(round(time.perf_counter()-t,3))") % (str(res), str(vendor), str(vendor))


def measure(label, env_extra, n=5):
    times = []
    for _ in range(n):
        env = dict(os.environ, **env_extra)
        out = subprocess.run([PY, '-c', probe], capture_output=True, text=True, env=env)
        assert out.returncode == 0, out.stderr
        times.append(float(out.stdout.strip()))
    print(f'{label:55s}: Importzeit Median {statistics.median(times):.3f}s  (Laeufe {times})')

measure('vendor ohne .pyc + PYTHONDONTWRITEBYTECODE=1 (wie App)', {'PYTHONDONTWRITEBYTECODE': '1'})
cache = work / 'pycache'
measure('PYTHONPYCACHEPREFIX=<Cache ausserhalb Bundle> (1. Lauf fuellt)', {'PYTHONPYCACHEPREFIX': str(cache)})
compileall.compile_dir(str(vendor), quiet=1)
compileall.compile_dir(str(res), quiet=1, maxlevels=0)
measure('vendor mit vorkompilierten .pyc + DONTWRITEBYTECODE', {'PYTHONDONTWRITEBYTECODE': '1'})
