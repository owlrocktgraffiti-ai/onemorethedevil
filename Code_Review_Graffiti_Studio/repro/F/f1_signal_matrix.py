"""F1: SIGTERM/SIGINT zu verschiedenen Zeitpunkten an native_bridge.py (Vorschau), OCR-Stub schlaeft.
Protokolliert Ereignisse, Exitcode, Latenz zwischen Signal und Prozessende sowie verwaiste Stub-Prozesse.
Aufruf: venv/bin/python repro/F/f1_signal_matrix.py
"""
import signal, time
from common import *

work, res = fresh('f1')
src = noise_photo(work / 'wand_ä.jpg')  # glattes Rauschbild ohne Papierkante -> analyze() ruft orientation(image)


def case(title, ocr_sleep, signals, settings=None):
    stub_orientation(res, sleep=ocr_sleep)
    b = Bridge(res, 'preview', dict(source=str(src), output=str(work / f'p_{time.time_ns()}.png'), settings=settings or {}), work)
    for at, sig in signals:
        b.signal_at(at, sig)
    b.wait()
    sent = [e['_t'] for e in b.events if str(e.get('type', '')).startswith('<SIG')]
    lat = round(b.seconds - sent[0], 2) if sent else None
    left = procs_matching(str(res / 'engine/orientation'))
    print(f'--- {title}')
    print(b.summary())
    print(f'Exitcode {b.returncode}; Ende nach {b.seconds}s; Latenz Signal->Ende {lat}s; verbliebene OCR-Prozesse: {len(left)}')
    if b.stderr.strip():
        print('stderr (Ende):', b.stderr.strip().splitlines()[-1][:200])
    return b


case('a) SIGTERM nach 0,05 s (waehrend der Importe, vor signal.signal in Zeile 9)', 0, [(0.05, signal.SIGTERM)])
case('b) SIGTERM nach 1,5 s waehrend OCR (Stub 20 s)', 20, [(1.5, signal.SIGTERM)])
case('c) SIGTERM nach 1,5 s, OCR-Stub haengt 60 s -> erst Timeout 45 s', 60, [(1.5, signal.SIGTERM)])
case('d) zweimal SIGTERM + SIGINT waehrend OCR (Stub 10 s)', 10, [(1.5, signal.SIGTERM), (3, signal.SIGTERM), (4, signal.SIGINT)])
case('e) Referenz ohne Signal (OCR-Stub 0 s)', 0, [])
