"""A6: eigenes Modell von run()/cancel()/receive()/BridgeJob (GraffitiStudio.swift:91-121,142,284-289).
Serielle Worker-Queue = 1 Thread; Hauptthread-Queue = main_q. Prozess = 'sleep' (ignoriert SIGTERM-Ende bis Checkpoint: hier 2 s Rest)."""
import threading,queue,subprocess,time,uuid,sys
main_q=queue.Queue();worker=queue.Queue()
def worker_loop():
    while True:worker.get()()
threading.Thread(target=worker_loop,daemon=True).start()
class BridgeJob:
    def __init__(s,cmd):s.cmd=cmd;s.lock=threading.Lock();s.cancelled=False;s.proc=None
    def cancel(s):
        with s.lock:
            s.cancelled=True
            if s.proc and s.proc.poll() is None:pass   # SIGTERM: Python laeuft bis zum naechsten Checkpoint weiter (hier: Rest des sleep)
    def start(s):
        with s.lock:
            if s.cancelled:return False
            s.proc=subprocess.Popen(s.cmd);return True
M=dict(token=None,busy=False,exportRunning=False,status='Bereit',job=None)
def receive(ev,tok,cmd):
    if M['token']!=tok:return
    if ev in('result','cancelled'):M['busy']=False;M['exportRunning']=False;M['status']=ev
def run(cmd,secs):
    if M['job']:M['job'].cancel()
    tok=uuid.uuid4();M['token']=tok;M['busy']=True;M['exportRunning']=cmd in('export','batch')
    nxt=BridgeJob(['sleep',str(secs)]);M['job']=nxt
    def block():
        if not nxt.start():return            # Zeile 106: guard try next.start() else{return}
        nxt.proc.wait()
        main_q.put(lambda:receive('cancelled' if nxt.cancelled else 'result',tok,cmd))
    worker.put(block)
def cancel():
    if M['job']:M['job'].cancel()
    if M['busy']:M['status']='Wird abgebrochen…'
def pump(t):
    end=time.time()+t
    while time.time()<end:
        try:main_q.get(timeout=.05)()
        except queue.Empty:pass
run('preview',2.0);pump(.3);run('export',1.0);pump(.1);cancel();pump(4)
print('Nach 4,4 s:',{k:M[k] for k in('busy','exportRunning','status')})
