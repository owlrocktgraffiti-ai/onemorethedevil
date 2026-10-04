import json,subprocess,sys,os,time,signal,tempfile
from pathlib import Path
V=Path(__file__).resolve().parent
PY='/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad/venv/bin/python'
RES=V/'Resources'
def bridge(cmd,request,env_extra=None,res=RES,signals=(),timeout=120):
    """Startet native_bridge wie Swift; signals=[(t,sig),...]; gibt (rc,events,raw_lines,stderr,dauer) zurueck"""
    rq=Path(tempfile.mkdtemp(dir=V/'work'))/'req.json'
    rq.write_text(json.dumps(request,ensure_ascii=False),encoding='utf-8')
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    if env_extra:env.update(env_extra)
    t0=time.monotonic()
    p=subprocess.Popen([PY,str(res/'native_bridge.py'),cmd,'--request',str(rq)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    for t,sig in signals:
        time.sleep(max(0,t-(time.monotonic()-t0)));p.send_signal(sig)
    out,err=p.communicate(timeout=timeout);dt=time.monotonic()-t0
    raw=out.split(b'\n');events=[]
    for line in raw:
        if not line:continue
        try:events.append(json.loads(line.decode('utf-8')))
        except Exception:events.append('<ungueltig>')
    return p.returncode,events,raw,err.decode('utf-8','replace'),dt
def swift_display(stderr):
    s=stderr[-2000:];return '\n'.join(s.split('\n')[:2])
(V/'work').mkdir(exist_ok=True)
