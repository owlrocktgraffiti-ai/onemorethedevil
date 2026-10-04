"""F5: Laufzeit-/Importfehler und was die Swift-Oberflaeche davon zeigt.
 a) Homebrew-python@3.14 ohne python-tk@3.14: _tkinter fehlt -> PIL.ImageTk (photo_prepare.py:6) scheitert
 b) Korrektur-Probe: dieselbe Umgebung, photo_prepare mit Lazy-Import von ImageTk (nur in einer KOPIE)
 c) Fallback-Interpreter mit anderer ABI: vendorte C-Erweiterung (cpython-314) wird von 3.12 nicht geladen;
    vendor/ steht vor site-packages und verdeckt das funktionierende numpy der Laufzeit
 d) ungueltige Einstellungen (native_bridge.py:20 ausserhalb try)
 e) Absturz in nativer Bibliothek (SIGSEGV waehrend der Analyse) -> stderr leer
Aufruf: venv/bin/python repro/F/f5_runtime_errors.py
"""
import importlib.machinery, os, signal, time
from common import *

work, res = fresh('f5')
src = noise_photo(work / 'wand.jpg')

# a) _tkinter fehlt (wie Homebrew python@3.14 ohne python-tk@3.14)
notk = work / 'ohne_tk'; notk.mkdir()
(notk / '_tkinter.py').write_text("raise ModuleNotFoundError(\"No module named '_tkinter'\", name='_tkinter')\n")
env = dict(os.environ, PYTHONPATH=str(notk))
for cmd, req in (('preview', dict(source=str(src), output=str(work / 'a.png'), settings={})),
                 ('prepare', dict(source=str(src), output=str(work / 'a_mask.png'), settings={})),
                 ('export', dict(source=str(src), output=str(work / 'Foto_a' / 'wand.png'), settings={}))):
    b = Bridge(res, cmd, req, work, env=env).wait()
    fin = b.events[-1] if b.events else None
    print(f'a) {cmd:8s} ohne _tkinter: Exitcode {b.returncode}; Endereignis {fin and {k: v for k, v in fin.items() if k != "_t"}}')
    print('   Swift zeigt:', repr(swift_error_display(b.stderr, fin)))

# b) Korrektur in Kopie: ImageTk erst in review() importieren
fixed = work / 'Resources_fix'
shutil.copytree(res, fixed)
pp = fixed / 'photo_prepare.py'
s = pp.read_text()
s = s.replace('from PIL import Image,ImageTk\n', 'from PIL import Image\n', 1)
s = s.replace(' import tkinter as tk\n', ' import tkinter as tk\n from PIL import ImageTk\n', 1)
pp.write_text(s)
b = Bridge(fixed, 'preview', dict(source=str(src), output=str(work / 'b.png'), settings={}), work, env=env).wait()
print(f'b) Lazy-Import, ohne _tkinter: Exitcode {b.returncode}; letztes Ereignis {b.events[-1]["type"]}')

# c) ABI-Simulation: vendor/numpy mit nur einer cpython-314-Erweiterung
print('c) Diese Laufzeit laedt Erweiterungen mit Endungen:', importlib.machinery.EXTENSION_SUFFIXES)
abi = work / 'Resources_abi'
shutil.copytree(res, abi)
(abi / 'vendor/numpy').mkdir(parents=True)
(abi / 'vendor/numpy/__init__.py').write_text('from . import _multiarray_umath\n')
(abi / 'vendor/numpy/_multiarray_umath.cpython-314-darwin.so').write_bytes(b'\xcf\xfa\xed\xfe')
b = Bridge(abi, 'preview', dict(source=str(src), output=str(work / 'c.png'), settings={}), work).wait()
last = [l for l in b.stderr.splitlines() if l.strip()][-1:]
print(f'c) Fallback-Interpreter 3.12 + vendor cp314: Exitcode {b.returncode}; JSON-Ereignisse {len(b.events)}; letzte stderr-Zeile {last}')
print('   Swift zeigt:', repr(swift_error_display(b.stderr, None)))
import numpy; print('   (das Laufzeit-eigene numpy waere ladbar gewesen:', numpy.__version__, ')')

# d) ungueltige Einstellungen
for title, settings in (('Rezept mit contrast=35', dict(values=dict(contrast=35))),
                        ('Rezept mit scale=3', dict(scale=3)),
                        ('gekreuzte Ecken aus MaskView', dict(corners=[[0, 0], [1, 1], [1, 0], [0, 1]]))):
    b = Bridge(res, 'preview', dict(source=str(src), output=str(work / 'd.png'), settings=settings), work).wait()
    last = [l for l in b.stderr.splitlines() if l.strip()][-1:]
    print(f'd) {title}: Exitcode {b.returncode}; JSON-Ereignisse {len(b.events)}; Ursache nur in stderr: {last}')
    print('   Swift zeigt:', repr(swift_error_display(b.stderr, None)))

# e) nativer Absturz (SIGSEGV) waehrend der Analyse: OCR-Stub schlaeft 3 s, dann SIGSEGV an Python
stub_orientation(res, sleep=3)
b = Bridge(res, 'preview', dict(source=str(src), output=str(work / 'e.png'), settings={}), work)
b.signal_at(1.0, signal.SIGSEGV)
b.wait()
print(f'e) SIGSEGV: Exitcode {b.returncode}; Ereignisse {[e["type"] for e in b.events]}; stderr {b.stderr.strip()[:200]!r}')
print('   Swift zeigt:', repr(swift_error_display(b.stderr, None)))
