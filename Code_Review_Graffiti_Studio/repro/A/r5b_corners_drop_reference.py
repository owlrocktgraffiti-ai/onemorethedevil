"""A3 (Ergaenzung): Sobald corners gesetzt sind (openMask setzt sie immer), verwirft adjustments.py:94-96 die
bekannte Referenzretusche - auch wenn "Bekannte Einzelretuschen" eingeschaltet bleibt. Nutzt die Kopie aus r5."""
from common import *
from PIL import Image
import numpy as np
work = HERE / 'work/r5'; res = work / 'Resources'; src = work / 'Wand.png'
for s, tag in [({}, 'Automatik'), (dict(corners=[[0, 0], [1, 0], [1, 1], [0, 1]], use_saved_retouches=True), 'nur Vollbild-Ecken (openMask+Uebernehmen, Schalter an)')]:
    ev = bridge(res, 'preview', dict(source=str(src), output=str(work / f'ref_{len(s)}.png'), settings=s), work)['events'][-1]
    b = np.array(Image.open(ev['result']['image']).convert('RGB')).astype(int)
    print(f'{tag:58s} Referenzretusche angewendet: {((b[:,:,1]>150)&(b[:,:,0]<80)).mean()>.9} | cached_correction im Plan: {"cached_correction" in ev["result"]["analysis"]}')
