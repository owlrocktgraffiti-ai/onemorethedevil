"""Fuehrt ein vorhandenes Testprogramm UNVERAENDERT, aber Anweisung fuer Anweisung aus,
damit nach einem Fehlschlag die folgenden Assertions trotzdem bewertet werden.

- Top-Level-Anweisungen (auch ';'-getrennte) werden einzeln kompiliert und ausgefuehrt.
- 'with tempfile.TemporaryDirectory() as td:' wird zu 'td=tempfile.mkdtemp()' + einzeln
  ausgefuehrtem Rumpf aufgeloest (sonst waere der ganze Block eine Anweisung).
- Ergebnis je Anweisung: OK / ASSERT-FEHLER / FEHLER / FOLGEFEHLER (NameError).

Aufruf: python stmt_runner.py <testdatei>   (CWD = Ordner, relativ zu dem der Test seine Pfade aufloest)
"""
import ast, sys, traceback, json, time

path = sys.argv[1]
src = open(path, encoding='utf-8').read()
lines = src.splitlines()
tree = ast.parse(src)


def flatten(body):
    out = []
    for node in body:
        if isinstance(node, ast.With) and len(node.items) == 1 and \
                ast.unparse(node.items[0].context_expr) == 'tempfile.TemporaryDirectory()':
            var = ast.unparse(node.items[0].optional_vars)
            assign = ast.parse(f'{var}=tempfile.mkdtemp()').body[0]
            ast.copy_location(assign, node); ast.fix_missing_locations(assign)
            assign.end_lineno = node.lineno
            out.append(assign)
            out.extend(flatten(node.body))
        else:
            out.append(node)
    return out


g = {'__name__': '__main__', '__file__': path}
results = []
for node in flatten(tree.body):
    seg = ast.get_source_segment(src, node) or ast.unparse(node)
    seg1 = ' '.join(seg.split())
    mod = ast.Module(body=[node], type_ignores=[])
    t0 = time.monotonic()
    try:
        exec(compile(mod, path, 'exec'), g)
        status, msg = 'OK', ''
    except AssertionError as e:
        status, msg = 'ASSERT-FEHLER', repr(e)[:300]
    except NameError as e:
        status, msg = 'FOLGEFEHLER', repr(e)[:300]
    except SystemExit as e:
        status, msg = 'SYSTEMEXIT', repr(e)
    except BaseException as e:
        status, msg = 'FEHLER', (type(e).__name__ + ': ' + str(e))[:400]
    dt = time.monotonic() - t0
    kind = 'ASSERT' if isinstance(node, ast.Assert) or 'assert ' in seg or 'AssertionError' in seg else 'STMT'
    results.append(dict(line=node.lineno, kind=kind, status=status, seconds=round(dt, 2), code=seg1[:160], error=msg))
    print(f'{path.split("/")[-1]}:{node.lineno:>3} [{kind:6}] {status:13} {seg1[:110]}' + (f'\n      -> {msg}' if msg else ''), flush=True)

print('ZUSAMMENFASSUNG', json.dumps({s: sum(r['status'] == s for r in results) for s in sorted({r['status'] for r in results})}))
