"""G10: SIGTERM waehrend laufender OCR (Stub engine/orientation, 8 s) bzw. waehrend KI-Kindprozess (Stub, 30 s)."""
import json, os, signal, subprocess, time
from PIL import Image
from vcommon import *
res = fresh_resources('g10'); inp = res.parent / 'in'; inp.mkdir()
Image.new('RGB', (900, 600), (90, 100, 120)).save(inp / 'foto.png')
pidfile = res.parent / 'child.pid'
ocr = res / 'engine/orientation'
ocr.write_text(f'#!{PY}\nimport os,time,json\nopen({str(pidfile)!r},"w").write(str(os.getpid()))\ntime.sleep(8)\nprint(json.dumps([{{"rotate":0,"score":0,"characters":0}}]))\n'); ocr.chmod(0o755)
ai = res / 'engine/realesrgan-ncnn-vulkan'
ai.write_text(f'#!{PY}\nimport os,time\nopen({str(pidfile)!r},"w").write(str(os.getpid()))\ntime.sleep(30)\n'); ai.chmod(0o755)
def alive(pid):
    try: os.kill(pid, 0); return True
    except OSError: return False
for label, settings in [('OCR laeuft', dict(mode='klassisch')), ('KI laeuft', dict(mode='ki'))]:
    if pidfile.exists(): pidfile.unlink()
    req = res.parent / 'req.json'; req.write_text(json.dumps(dict(source=str(inp / 'foto.png'), output=str(res.parent / 'p.png'), settings=settings)))
    p = subprocess.Popen([PY, str(res / 'native_bridge.py'), 'preview', '--request', str(req)], stdout=subprocess.PIPE, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    # warten bis der Kindprozess laeuft (bei KI erst nach der OCR)
    t0 = time.monotonic()
    while True:
        if pidfile.exists() and pidfile.read_text():
            pid = int(pidfile.read_text())
            # bei KI: OCR-Stub schreibt zuerst; warten bis der KI-Stub die Datei ueberschreibt
            if label.startswith('KI'):
                time.sleep(9)
                pid = int(pidfile.read_text())
            break
        time.sleep(.05)
    time.sleep(.5)
    t = time.monotonic(); p.send_signal(signal.SIGTERM)
    out, _ = p.communicate(timeout=60)
    dt = time.monotonic() - t
    last = [json.loads(l)['type'] for l in out.splitlines() if l.startswith('{')][-1]
    print(f'{label}: SIGTERM -> Bruecke beendet nach {dt:.1f}s, letztes Ereignis {last!r}, Kind {pid} noch aktiv: {alive(pid)}')
