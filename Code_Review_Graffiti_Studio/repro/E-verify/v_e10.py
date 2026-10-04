import subprocess,time,json,os,signal
from pathlib import Path
V=Path(__file__).resolve().parent;PY=str(V.parent.parent/'venv/bin/python')
req=V/'out/v_e10_req.json';req.write_text(json.dumps(dict(source=str(V/'out/v_zug.png'),output=str(V/'out/v_e10_prev.png'),settings={})))
env=dict(os.environ,VSTUB_SLEEP='6',VSTUB_ROT='0')
t=time.monotonic();p=subprocess.Popen([PY,str(V/'Res_ocr/native_bridge.py'),'preview','--request',str(req)],stdout=subprocess.PIPE,text=True,env=env)
time.sleep(1.0);p.send_signal(signal.SIGTERM);ts=time.monotonic()-t
out=p.communicate()[0];te=time.monotonic()-t
print(f'SIGTERM nach {ts:.2f} s, Prozessende nach {te:.2f} s; Ereignisse:',[json.loads(l)['type'] for l in out.splitlines() if l.strip()])
