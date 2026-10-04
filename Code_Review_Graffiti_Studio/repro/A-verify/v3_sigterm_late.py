"""A1-Gegenprobe: SIGTERM spaeter im Ordnerexport -> bleiben fertige Bilder erhalten?"""
import sys,time,json,subprocess,signal
from pathlib import Path
sys.argv=[sys.argv[0]]
HERE=Path(__file__).resolve().parent;W=HERE/'work';R=HERE/'Resources'
files=sorted(str(p) for p in W.glob('z*.jpg'))
out=W/'Ordner_spaet';rq=W/'req_late.json'
rq.write_text(json.dumps(dict(files=files,output=str(out),settings=dict(values={},mode='klassisch',scale=1),per_photo={})))
t=time.monotonic();p=subprocess.Popen([sys.executable,str(R/'native_bridge.py'),'batch','--request',str(rq)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
seen=[]
for line in p.stdout:
    e=json.loads(line);seen.append(e)
    if e['type']=='progress' and e['stage'].startswith('2/'):
        p.send_signal(signal.SIGTERM);print(f'SIGTERM bei Stufe "{e["stage"]}" nach {time.monotonic()-t:.1f}s');break
for line in p.stdout:seen.append(json.loads(line))
p.wait()
print('Exit',p.returncode,'letztes Ereignis',seen[-1]['type'])
print('Inhalt:',sorted(x.name for x in out.iterdir()),'| ZIP:',out.with_suffix('.zip').exists())
# Signalbehandlung waehrend subprocess.run (OCR-Analogon, analysis.py:41)
code='''import signal,threading,subprocess,time,sys
ev=threading.Event();signal.signal(signal.SIGTERM,lambda *_:ev.set())
t=time.monotonic();subprocess.run(["sleep","4"],timeout=45);print(f"subprocess.run endete nach {time.monotonic()-t:.1f}s, Abbruch-Event gesetzt={ev.is_set()}")'''
q=subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,text=True);time.sleep(0.5);q.send_signal(signal.SIGTERM);print('OCR-Analogon (SIGTERM nach 0,5 s):',q.communicate()[0].strip())
