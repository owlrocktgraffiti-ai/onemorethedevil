"""Gemeinsame Hilfen für Bereich D. Importiert die KOPIE unter repro/D/Resources."""
import sys, struct, io
from pathlib import Path
HERE = Path(__file__).resolve().parent
RES = HERE / 'Resources'
OUT = HERE / 'out'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(RES))


def _s15(v):
    return struct.pack('>i', int(round(v * 65536)))


def _xyz_tag(x, y, z):
    return b'XYZ ' + b'\0' * 4 + _s15(x) + _s15(y) + _s15(z)


def _desc_tag(text):
    t = text.encode('ascii') + b'\0'
    body = b'desc' + b'\0' * 4 + struct.pack('>I', len(t)) + t
    body += b'\0' * 4 + b'\0' * 4  # unicode lang + count
    body += b'\0' * 2 + b'\0' + b'\0' * 67  # scriptcode
    return body


def _text_tag(text):
    return b'text' + b'\0' * 4 + text.encode('ascii') + b'\0'


def _curv_gamma(g):
    return b'curv' + b'\0' * 4 + struct.pack('>I', 1) + struct.pack('>H', int(round(g * 256)))


def display_p3_like_icc(name='Display P3 (synthetisch, Gamma 2.2)'):
    """Matrix/TRC-ICC-v2 mit Display-P3-Primärvalenzen (D50-adaptiert, Werte aus Apples Profil)."""
    tags = [
        (b'desc', _desc_tag(name)),
        (b'cprt', _text_tag('public domain test profile')),
        (b'wtpt', _xyz_tag(0.9642, 1.0, 0.8249)),
        (b'rXYZ', _xyz_tag(0.5151, 0.2412, -0.0011)),
        (b'gXYZ', _xyz_tag(0.2920, 0.6922, 0.0419)),
        (b'bXYZ', _xyz_tag(0.1571, 0.0666, 0.7841)),
        (b'rTRC', _curv_gamma(2.2)),
        (b'gTRC', _curv_gamma(2.2)),
        (b'bTRC', _curv_gamma(2.2)),
    ]
    n = len(tags)
    offset = 128 + 4 + 12 * n
    table = b''
    data = b''
    for sig, body in tags:
        while (offset + len(data)) % 4:
            data += b'\0'
        table += sig + struct.pack('>II', offset + len(data), len(body))
        data += body
    while (offset + len(data)) % 4:
        data += b'\0'
    size = offset + len(data)
    header = struct.pack('>I', size) + b'lcms' + bytes([2, 0x10, 0, 0]) + b'mntr' + b'RGB ' + b'XYZ '
    header += struct.pack('>6H', 2026, 1, 1, 0, 0, 0) + b'acsp' + b'APPL' + b'\0' * 4 + b'\0' * 4 + b'\0' * 4 + b'\0' * 8
    header += struct.pack('>I', 0) + _s15(0.9642) + _s15(1.0) + _s15(0.8249) + b'test'
    header += b'\0' * (128 - len(header))
    return header + struct.pack('>I', n) + table + data
