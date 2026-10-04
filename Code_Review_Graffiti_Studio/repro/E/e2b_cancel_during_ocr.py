"""Abbruch (SIGTERM wie BridgeJob.cancel) während laufender OCR: Python-Prozess läuft weiter bis OCR fertig."""
import subprocess,sys,time,json,os,signal
from pathlib import Path
E=Path(__file__).resolve().parent;RES=E/'Resources_ocr';OUT=E/'out'
src=OUT/'e2_12mp.jpg'
req=OUT/'e2b_req.json';req.write_text(json.dumps(dict(source=str(src),output=str(OUT/'e2b_prev.png'),settings={})))
env=dict(os.environ,OCR_STUB_SLEEP='8',OCR_STUB_LOG=str(OUT/'e2b_ocr.log'))
(OUT/'e2b_ocr.log').unlink(missing_ok=True)
procs=[]
start=time.perf_counter()
# simuliert drei schnelle Reglerbewegungen im Abstand von 0,5 s: jeweils alter Prozess SIGTERM, neuer Prozess gestartet
for i in range(3):
    if procs:procs[-1].send_signal(signal.SIGTERM)
    procs.append(subprocess.Popen([sys.executable,str(RES/'native_bridge.py'),'preview','--request',str(req)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env))
    time.sleep(.5)
time.sleep(1.0)
alive=[p.poll() is None for p in procs]
print(f'{time.perf_counter()-start:5.2f} s nach Start: noch laufende Python-Prozesse: {sum(alive)} von {len(procs)} (die ersten zwei wurden per SIGTERM abgebrochen)')
for i,p in enumerate(procs):
    out,err=p.communicate()
    last=[json.loads(l)['type'] for l in out.splitlines() if l.strip()]
    print(f'Prozess {i+1}: beendet nach {time.perf_counter()-start:5.2f} s, Ereignisse={last}')
print('OCR-Aufrufe:',len((OUT/'e2b_ocr.log').read_text().splitlines()))
