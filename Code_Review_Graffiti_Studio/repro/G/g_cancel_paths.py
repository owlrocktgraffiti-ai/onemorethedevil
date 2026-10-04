"""Testluecke 'Abbruch': Die ausgelieferten Tests pruefen nur render_one mit VORHER gesetztem Event und run_model direkt.
Hier der echte Weg der App: SIGTERM an native_bridge.py (Swift BridgeJob.cancel -> process.terminate, Swift:287).
(1) waehrend Stub-KI-Modell laeuft, (2) waehrend Stub-OCR (engine/orientation) laeuft."""
import sys, os, time, json, signal, subprocess
sys.path.insert(0, '/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/repro/G')
from common import *
from PIL import Image

def alive(pid):
    try: os.kill(pid, 0)
    except ProcessLookupError: return False
    st = open(f'/proc/{pid}/stat').read().split()[2] if os.path.exists(f'/proc/{pid}/stat') else '?'
    return st != 'Z'

def scenario(name, stubname, settings):
    res = fresh_resources('cancel_' + name); wd = res.parent
    pidfile = wd / 'child.pid'
    stub = res / 'engine' / stubname
    stub.write_text(f'#!/bin/sh\necho $$ > {pidfile}\nexec sleep 30\n'); stub.chmod(0o755)
    Image.new('RGB', (800, 600), (90, 120, 150)).save(wd / 'f.jpg')
    req = wd / 'req.json'; req.write_text(json.dumps(dict(source=str(wd / 'f.jpg'), output=str(wd / 'p.png'), settings=settings)))
    p = subprocess.Popen([PY, str(res / 'native_bridge.py'), 'preview', '--request', str(req)], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    t0 = time.monotonic()
    while not pidfile.exists() and time.monotonic() - t0 < 30: time.sleep(.05)
    child = int(pidfile.read_text()); time.sleep(.3)
    t1 = time.monotonic(); p.send_signal(signal.SIGTERM)
    try: out, _ = p.communicate(timeout=60)
    except subprocess.TimeoutExpired: p.kill(); out, _ = p.communicate()
    dt = time.monotonic() - t1
    last = [json.loads(l)['type'] for l in out.splitlines() if l.strip()][-1:]
    print(f'{name}: Kindprozess {stubname} gestartet nach {t1-t0:.1f}s; SIGTERM -> Bruecke beendet nach {dt:.1f}s, letztes Ereignis {last}, '
          f'Kind {child} noch aktiv: {alive(child)}')
    if alive(child): os.kill(child, signal.SIGKILL)

scenario('KI', 'realesrgan-ncnn-vulkan', dict(mode='ki', scale=2))
scenario('OCR', 'orientation', dict(mode='klassisch', scale=1))
