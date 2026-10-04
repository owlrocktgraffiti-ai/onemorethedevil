"""A1 (Modell): zeilengetreue Nachbildung von StudioModel.run/cancel/receive und BridgeJob
(GraffitiStudio.swift:89-143, 284-289) mit serieller Queue. Echte Python-Prozesse werden durch
'sleep'-Kindprozesse ersetzt, die SIGTERM wie native_bridge.py erst am naechsten Checkpoint beachten.
Kein Swift-Lauf - dient nur dazu, den Codepfad nachvollziehbar zu machen.
"""
import threading, queue, subprocess, time, uuid, sys

main_q = queue.Queue()                       # DispatchQueue.main
worker_q = queue.Queue()                     # serielle DispatchQueue 'worker'
threading.Thread(target=lambda: [f() for f in iter(worker_q.get, None)], daemon=True).start()

# Kindprozess: ignoriert SIGTERM bis zum "Checkpoint" nach 'busy_seconds' (wie OCR/Analyse)
CHILD = ("import signal,sys,time,json;c=[False];signal.signal(signal.SIGTERM,lambda *a:c.__setitem__(0,True));"
         "time.sleep(float(sys.argv[1]));print(json.dumps({'type':'cancelled' if c[0] else 'result'}),flush=True)")

class BridgeJob:
    def __init__(self, secs):
        self.secs = secs; self.proc = None; self.lock = threading.Lock(); self.cancelled = False
    def cancel(self):
        with self.lock:
            self.cancelled = True
            if self.proc and self.proc.poll() is None: self.proc.terminate()
    def start(self):
        with self.lock:
            if self.cancelled: return False
            self.proc = subprocess.Popen([sys.executable, '-c', CHILD, str(self.secs)], stdout=subprocess.PIPE); return True

class Model:
    def __init__(self): self.job = None; self.token = None; self.busy = False; self.exportRunning = False; self.status = 'Bereit'
    def run(self, command, secs):
        if self.job: self.job.cancel()
        cur = uuid.uuid4(); self.token = cur; self.busy = True; self.exportRunning = command in ('export', 'batch')
        nxt = BridgeJob(secs); self.job = nxt
        def block():
            if not nxt.start(): return                     # Swift: guard try next.start() else{return}
            final = False
            for line in nxt.proc.stdout:
                import json; ev = json.loads(line); final = final or ev['type'] in ('result', 'error', 'cancelled')
                main_q.put(lambda ev=ev: self.receive(ev, cur))
            nxt.proc.wait()
            if not final: main_q.put(lambda: self.receive({'type': 'cancelled'}, cur) if self.token == cur else None)
        worker_q.put(block)
    def receive(self, ev, cur):
        if self.token != cur: return
        if ev['type'] in ('result', 'cancelled'): self.busy = False; self.exportRunning = False; self.status = ev['type']
    def cancel(self):
        if self.job: self.job.cancel()
        if self.busy: self.status = 'Wird abgebrochen…'

def pump(seconds):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        try: main_q.get(timeout=.05)()
        except queue.Empty: pass

m = Model()
m.run('preview', 6)          # Vorschau laeuft (z. B. OCR)
pump(1.0)
m.run('export', 3)           # "Foto exportieren": Vorschau erhaelt SIGTERM, Export wartet in der seriellen Queue
pump(0.5)
m.cancel()                   # "Abbrechen" kurz danach
pump(12)                     # genug Zeit, damit alles abgearbeitet ist
print('Nach 12 s:', dict(busy=m.busy, exportRunning=m.exportRunning, status=m.status))
