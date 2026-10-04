"""F6: Kodierung von Request-Datei und stdout-Protokoll je nach Locale der App-Umgebung.
GUI-Start unter macOS: launchd setzt meist kein LANG -> Python startet mit C-Locale.
 - ohne LANG / LANG=C / LC_ALL=C / LC_ALL=POSIX, Pfad mit Umlauten und Emoji
 - Nicht-UTF-8-Locale (de_DE.ISO-8859-1 via LOCPATH erzeugt), um die Wirkung zu zeigen
Aufruf: venv/bin/python repro/F/f6_encoding.py
"""
import os
from common import *

work, res = fresh('f6')
folder = work / 'Wände_Köln…_🎨'; folder.mkdir()
src = noise_photo(folder / 'Gleis_Ä.jpg')
base_env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': os.environ.get('HOME', '/root')}
LOC = str(HERE / 'locale')

for label, extra in (('ohne LANG (wie GUI-Start)', {}), ('LANG=C', {'LANG': 'C'}), ('LC_ALL=C', {'LC_ALL': 'C'}),
                     ('LC_ALL=POSIX', {'LC_ALL': 'POSIX'})):
    env = dict(base_env, **extra)
    out = folder / f'Ergebnis_{label[:6].strip()}' / 'Gleis_Ä.png'
    b = Bridge(res, 'export', dict(source=str(src), output=str(out), settings=dict(mode='klassisch', scale=1)), work, env=env).wait()
    fin = b.events[-1]
    ok = fin['type'] == 'result' and Path(fin['result']['zip']).exists()
    print(f'{label:28s}: Exitcode {b.returncode}; Endereignis {fin["type"]}; ZIP vorhanden {ok}; verworfene Zeilen {sum(e["type"].startswith("<von") for e in b.events)}')

# Nicht-UTF-8-Locale: ASCII-Pfad, damit nur das stdout-Protokoll betroffen ist
env = dict(base_env, LOCPATH=LOC, LC_ALL='de_DE.ISO-8859-1')
asc = noise_photo(work / 'gleis.jpg')
b = Bridge(res, 'export', dict(source=str(asc), output=str(work / 'Foto_latin1' / 'gleis.png'), settings=dict(mode='klassisch', scale=1)), work, env=env).wait()
kinds = [e['type'] for e in b.events]
print(f'LC_ALL=de_DE.ISO-8859-1      : Exitcode {b.returncode}; Ereignisse {kinds}')
print('   ZIP auf Platte:', (work / 'Foto_latin1').with_suffix('.zip').exists(), '| Swift erhaelt ein result:', 'result' in kinds,
      '-> zeigt:', repr(swift_error_display(b.stderr, None)) if 'result' not in kinds else '')
# Request-Datei: Swift schreibt UTF-8; Path.read_text() nutzt die Locale-Kodierung
raw = str(src).encode('utf-8')
print('   read_text unter ISO-8859-1 liefert Pfad:', raw.decode('latin-1')[-30:], '(macOS-Dateisystem ist UTF-8 -> Datei nicht gefunden)')
