"""D2: Eingabeformate durch graffiti.read_image (Einstieg jeder Vorschau/jedes Exports)."""
import numpy as np, cv2, warnings
from PIL import Image
import common
from graffiti import read_image

OUT = common.OUT / 't2'
OUT.mkdir(exist_ok=True)
W, H = 256, 64
ramp16 = np.tile(np.linspace(0, 65535, W).astype(np.uint16), (H, 1))
expected8 = np.tile(np.linspace(0, 255, W), (H, 1))


def report(name, path, expect=None, note=''):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        try:
            with Image.open(path) as im:
                mode = im.mode
            rgb = np.array(read_image(path)).astype(float)
        except Exception as e:
            print(f'{name:34s} FEHLER {type(e).__name__}: {e}'); return
    msg = f'{name:34s} Pillow-Modus={mode:6s} RGB-Mittel={rgb.mean(axis=(0,1)).round(1)}'
    if expect is not None:
        g = rgb.mean(axis=2)
        msg += f' Spalte 64/128/192 -> {g[:, 64].mean():.0f}/{g[:, 128].mean():.0f}/{g[:, 192].mean():.0f} (erwartet {expect[:,64].mean():.0f}/{expect[:,128].mean():.0f}/{expect[:,192].mean():.0f}); Anteil=255: {(g>=254.5).mean():.2f}'
    if w: msg += ' | Warnung: ' + str(w[0].message)[:90]
    print(msg + (' ' + note if note else ''))
    return rgb


# 16-Bit-Graustufen-PNG (z. B. Scanner/Lightroom-Export)
p = OUT / 'gray16.png'; cv2.imwrite(str(p), ramp16); report('PNG 16 Bit grau', p, expected8)
# 16-Bit-Graustufen-TIFF
p = OUT / 'gray16.tif'; cv2.imwrite(str(p), ramp16); report('TIFF 16 Bit grau', p, expected8)
# 48-Bit-RGB-PNG und -TIFF
rgb16 = np.dstack([ramp16] * 3)
p = OUT / 'rgb48.png'; cv2.imwrite(str(p), rgb16); report('PNG 48 Bit RGB', p, expected8)
p = OUT / 'rgb48.tif'; cv2.imwrite(str(p), rgb16); report('TIFF 48 Bit RGB', p, expected8)
# 32-Bit-Float-TIFF (0..1)
p = OUT / 'float.tif'; Image.fromarray((ramp16 / 65535).astype(np.float32), 'F').save(p); report('TIFF 32 Bit float (0..1)', p, expected8)
# RGBA mit transparentem Hintergrund (Freisteller): RGB unter Alpha=0 ist schwarz
a = np.zeros((H, W, 4), np.uint8); a[:, :W // 2] = (230, 60, 60, 255)
p = OUT / 'rgba.png'; Image.fromarray(a, 'RGBA').save(p); r = report('PNG RGBA, Hälfte transparent', p)
print('   transparente Hälfte wird zu', r[:, -1].mean(0).round(), '(Apple-Vorschau zeigt sie transparent/hell)')
# LA
la = np.zeros((H, W, 2), np.uint8); la[:, :W // 2] = (200, 255)
p = OUT / 'la.png'; Image.fromarray(la, 'LA').save(p); r = report('PNG LA, Hälfte transparent', p); print('   transparente Hälfte ->', r[:, -1].mean(0).round())
# P mit Transparenz
pal = Image.new('P', (W, H), 0); pal.putpalette([0, 0, 0, 255, 0, 0] + [0] * 762); pal.paste(1, (0, 0, W // 2, H)); pal.info['transparency'] = 0
p = OUT / 'pal_trans.png'; pal.save(p, transparency=0); r = report('PNG Palette mit Transparenz', p); print('   transparente Hälfte ->', r[:, -1].mean(0).round())
# CMYK-JPEG (Druckvorstufe/Scan)
cmyk = Image.new('CMYK', (W, H), (0, 0, 0, 0)); cmyk.paste((0, 200, 200, 30), (0, 0, W // 2, H))
p = OUT / 'cmyk.jpg'; cmyk.save(p, quality=95); r = report('JPEG CMYK (ohne Profil)', p); print('   CMYK(0,78%,78%,12%) ->', r[:, 10].mean(0).round(), '(naive Umrechnung)')
