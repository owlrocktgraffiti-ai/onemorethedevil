"""F3: studio_backend.run_model mit Stub-Modellen (kooperativ, SIGTERM-ignorierend, Enkelprozess, Timeout)
und KI-Pfad ueber die Bruecke (Abbruch, SIGKILL der Bruecke -> verwaister Modellprozess).
Aufruf: venv/bin/python repro/F/f3_run_model.py
"""
import signal, subprocess, sys, threading, time
from common import *

work, res = fresh('f3')
sys.path.insert(0, str(res))
from studio_backend import run_model

stub = stub_realesrgan(res, 'sleep', 30)


def call(behaviour, cancel_after=None, timeout=600):
    stub_realesrgan(res, behaviour, 30)
    cancel = threading.Event(); seen = []
    if cancel_after is not None:
        threading.Timer(cancel_after, cancel.set).start()
    t0 = time.monotonic()
    try:
        r = run_model([str(stub), '-i', 'x', '-o', 'y'], cancel, lambda s, f: seen.append((s, f)), timeout=timeout)
        outcome = f'Rueckgabe {r[0]}'
    except BaseException as e:
        outcome = f'{type(e).__name__}: {e}'
    dt = round(time.monotonic() - t0, 2)
    time.sleep(0.3)
    left = procs_matching('realesrgan-ncnn-vulkan') + [p for p in procs_matching('sleep 30.5')]
    print(f'{behaviour:10s} cancel={cancel_after} timeout={timeout}: {outcome}; Dauer {dt}s; Fortschritt {sorted(set(seen))}; verbliebene Prozesse {[(p, c[-40:], pp) for p, c, pp in left]}')
    for p, c, pp in left:
        try: os.kill(p, signal.SIGKILL)
        except OSError: pass


call('sleep', cancel_after=0.5)
call('ignore', cancel_after=0.5)
call('grandchild', cancel_after=0.5)
call('sleep', timeout=2.5)

# Ueber die Bruecke: Export mit mode='ki', kleines Bild (use_ai), Stub schlaeft 30 s
src = noise_photo(work / 'klein.jpg', size=(800, 600))
for title, sig in (('SIGTERM an Bruecke', signal.SIGTERM), ('SIGKILL an Bruecke (z. B. Sofort beenden/Speicherdruck)', signal.SIGKILL)):
    stub_realesrgan(res, 'sleep', 30)
    b = Bridge(res, 'preview', dict(source=str(src), output=str(work / f'p_{sig}.png'), settings=dict(mode='ki', scale=2)), work)
    started = []
    def on_event(br, ev, sig=sig):
        if ev.get('stage') == 'Lokale KI arbeitet' and not started:
            started.append(br.t()); br.proc.send_signal(sig); br.events.append({'type': f'<{signal.Signals(sig).name} gesendet>', '_t': br.t()})
    b.callbacks.append(on_event)
    b.wait(timeout=120)
    time.sleep(0.5)
    left = procs_matching('realesrgan-ncnn-vulkan')
    print('---', title); print(b.summary())
    print(f'Exitcode {b.returncode}; Ende nach {b.seconds}s; verbliebene Modellprozesse: {[(p, pp) for p, c, pp in left]}')
    for p, c, pp in left:
        os.kill(p, signal.SIGKILL)

# Fortschritt im KI-Pfad (Stub 'ok', schreibt Ergebnis nach 6 s Schlaf -> hier ohne Schlaf, dafuer Stub 'sleep' 7 s + Abbruch nein)
stub_realesrgan(res, 'sleep', 7)
b = Bridge(res, 'preview', dict(source=str(src), output=str(work / 'p_progress.png'), settings=dict(mode='ki', scale=2)), work).wait()
print('--- KI-Stub ohne Ausgabe (7 s), ohne Abbruch'); print(b.summary())
