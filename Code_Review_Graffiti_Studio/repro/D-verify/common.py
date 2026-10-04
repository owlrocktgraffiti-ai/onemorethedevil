import sys,os
from pathlib import Path
V=Path(__file__).resolve().parent
RES=V/'Resources'
sys.path.insert(0,str(RES))
os.chdir(V)
OUT=V/'out';OUT.mkdir(exist_ok=True)
