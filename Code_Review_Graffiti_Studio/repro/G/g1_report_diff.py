"""Vergleicht die AUSGELIEFERTEN Pruefberichte mit den Berichten, die die AUSGELIEFERTEN Testprogramme schreiben
(erzeugt in repro/G/runB durch unveraenderte Ausfuehrung der Tests)."""
import json
B='/tmp/claude-0/-home-user-onemorethedevil/6ce71caf-ac92-56ea-8654-f76e736d54cd/scratchpad'
pairs=[('Pruefung.json', B+'/pkg/Pruefung.json', B+'/repro/G/runB/outputs/Graffiti_Studio_Mac/Pruefung.json'),
       ('Backend_Pruefung.json', B+'/pkg/Graffiti Studio.app/Contents/Resources/Backend_Pruefung.json', B+'/repro/G/runB/outputs/Graffiti_Studio_Mac/Graffiti Studio.app/Contents/Resources/Backend_Pruefung.json')]
for name,shipped,generated in pairs:
    s=json.load(open(shipped));g=json.load(open(generated))
    print('==',name)
    print('  nur im ausgelieferten Bericht:', {k:s[k] for k in s.keys()-g.keys()})
    print('  nur im vom Test erzeugten Bericht:', {k:g[k] for k in g.keys()-s.keys()})
    print('  gleiche Schluessel mit anderem Wert:', {k:(s[k],g[k]) for k in s.keys()&g.keys() if s[k]!=g[k]})
    print('  checks identisch:', s['checks']==g['checks'])
