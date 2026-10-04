"""G12: Bruecke ohne tkinter (simuliert fehlendes python-tk@3.14)."""
import json
from PIL import Image
from vcommon import *
res = fresh_resources('g12'); inp = res.parent / 'in'; inp.mkdir(); Image.new('RGB', (300, 200), (90, 100, 120)).save(inp / 'f.png')
for cmd in ('preview', 'prepare', 'batch'):
    req = dict(source=str(inp / 'f.png'), output=str(res.parent / f'{cmd}.png'), settings={}, files=[str(inp / 'f.png')])
    if cmd == 'batch': req['output'] = str(res.parent / 'batch')
    code, ev, err = bridge(res, cmd, req, env_extra=dict(PYTHONPATH=str(HERE / 'no_tk')))
    print(cmd, 'exit', code, ev[-1] if ev else err[-200:])
