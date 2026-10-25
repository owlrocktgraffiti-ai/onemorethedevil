#!/usr/bin/env python3
"""CLI fuer das Team-Board in Trello.

    python3 trello/trello_cli.py whoami
    python3 trello/trello_cli.py setup
    python3 trello/trello_cli.py add "Rechnungen pruefen" --fuer max --bis freitag
    python3 trello/trello_cli.py bulk tasks.json
    python3 trello/trello_cli.py show --fuer max --offen
    python3 trello/trello_cli.py done "Rechnungen"

Alle Befehle lesen trello/team.json (Vorlage: trello/team.example.json).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dates import DateParseError, parse_due  # noqa: E402
from trello_client import LABEL_COLORS, TrelloClient, TrelloError  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "team.json"


# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------

def load_config(path: Path) -> dict:
    if not path.is_file():
        raise TrelloError(
            f"Konfiguration fehlt: {path}\n"
            f"Vorlage kopieren:  cp {HERE / 'team.example.json'} {path}"
        )
    cfg = json.loads(path.read_text(encoding="utf-8"))
    cfg.setdefault("layout", "members")
    cfg.setdefault("statuses", ["Backlog", "To Do", "In Arbeit", "Erledigt"])
    cfg.setdefault("done_list", "Erledigt")
    cfg.setdefault("inbox_list", cfg["statuses"][0])
    cfg.setdefault("priorities", {})
    cfg.setdefault("members", [])
    if not cfg.get("board"):
        raise TrelloError(f"In {path} fehlt der Eintrag 'board'.")
    if cfg["layout"] not in ("members", "status"):
        raise TrelloError("'layout' muss 'members' oder 'status' sein.")
    return cfg


def target_lists(cfg: dict) -> list[str]:
    """Die Listen, die das Board laut Konfiguration haben soll — in Reihenfolge."""
    if cfg["layout"] == "status":
        return list(cfg["statuses"])
    names = [cfg["inbox_list"]]
    names += [m.get("name") or m["alias"] for m in cfg["members"]]
    if cfg["done_list"] not in names:
        names.append(cfg["done_list"])
    # Duplikate entfernen, Reihenfolge erhalten
    return list(dict.fromkeys(names))


# --------------------------------------------------------------------------
# Auflösen von Namen zu Trello-IDs
# --------------------------------------------------------------------------

def resolve_board(client: TrelloClient, cfg: dict) -> dict:
    board = client.find_board(cfg["board"])
    if not board:
        raise TrelloError(
            f"Board {cfg['board']!r} nicht gefunden. Einmal anlegen mit:  setup"
        )
    return board


def member_entry(cfg: dict, alias: str) -> dict:
    key = alias.strip().casefold()
    for m in cfg["members"]:
        candidates = {
            m.get("alias", "").casefold(),
            (m.get("name") or "").casefold(),
            (m.get("trello_username") or "").casefold(),
            (m.get("email") or "").casefold(),
        }
        if key in candidates - {""}:
            return m
        # Auch Vorname allein zulassen ("max" fuer "Max Mustermann")
        if (m.get("name") or "").casefold().split()[:1] == [key]:
            return m
    known = ", ".join(m.get("alias", "?") for m in cfg["members"]) or "(keine)"
    raise TrelloError(f"Person {alias!r} steht nicht in team.json. Bekannt: {known}")


def resolve_member_id(client: TrelloClient, board_id: str, cfg: dict, alias: str) -> str | None:
    """Trello-Member-ID fuer einen Alias, oder None wenn die Person noch nicht beigetreten ist."""
    entry = member_entry(cfg, alias)
    wanted = {
        (entry.get("trello_username") or "").casefold(),
        (entry.get("name") or "").casefold(),
        entry.get("alias", "").casefold(),
    } - {""}
    for bm in client.board_members(board_id):
        if (bm.get("username") or "").casefold() in wanted:
            return bm["id"]
        if (bm.get("fullName") or "").casefold() in wanted:
            return bm["id"]
    return None


def find_list(client: TrelloClient, board_id: str, name: str) -> dict:
    wanted = name.strip().casefold()
    lists = client.board_lists(board_id)
    for lst in lists:
        if lst["name"].strip().casefold() == wanted:
            return lst
    for lst in lists:  # Teiltreffer als Komfort
        if wanted in lst["name"].casefold():
            return lst
    available = ", ".join(l["name"] for l in lists)
    raise TrelloError(f"Liste {name!r} gibt es nicht. Vorhanden: {available}")


def list_for_task(client: TrelloClient, board_id: str, cfg: dict,
                  assignee: str | None, explicit_list: str | None) -> dict:
    if explicit_list:
        return find_list(client, board_id, explicit_list)
    if cfg["layout"] == "members" and assignee:
        entry = member_entry(cfg, assignee)
        return find_list(client, board_id, entry.get("name") or entry["alias"])
    return find_list(client, board_id, cfg["inbox_list"])


# --------------------------------------------------------------------------
# Befehle
# --------------------------------------------------------------------------

def cmd_whoami(client: TrelloClient, cfg: dict, args) -> int:
    me = client.whoami()
    print(f"Angemeldet als: {me.get('fullName')} (@{me.get('username')})")
    orgs = client.my_organizations()
    print(f"Workspaces: {', '.join(o['displayName'] for o in orgs) or '(keine)'}")
    boards = client.my_boards()
    print(f"Boards ({len(boards)}/10 im Free-Plan pro Workspace):")
    for b in boards:
        print(f"  - {b['name']}  {b['url']}")
    return 0


def cmd_setup(client: TrelloClient, cfg: dict, args) -> int:
    board = client.find_board(cfg["board"])
    if board:
        print(f"Board {cfg['board']!r} existiert schon: {board['url']}")
    else:
        org_id = None
        if args.workspace:
            for o in client.my_organizations():
                if args.workspace.casefold() in (o["displayName"].casefold(), o["name"].casefold()):
                    org_id = o["id"]
                    break
            if not org_id:
                raise TrelloError(f"Workspace {args.workspace!r} nicht gefunden.")
        board = client.create_board(cfg["board"], org_id)
        print(f"Board angelegt: {board['name']}  {board['url']}")

    for pos, name in enumerate(target_lists(cfg), start=1):
        existing = {l["name"].casefold() for l in client.board_lists(board["id"])}
        if name.casefold() in existing:
            print(f"  Liste ok:       {name}")
        else:
            client.create_list(board["id"], name, pos=pos * 1000)
            print(f"  Liste angelegt: {name}")

    for idx, (label, color) in enumerate(cfg["priorities"].items()):
        if color not in LABEL_COLORS:
            color = LABEL_COLORS[idx % len(LABEL_COLORS)]
        client.ensure_label(board["id"], label, color)
        print(f"  Label ok:       {label} ({color})")

    if args.invite:
        for m in cfg["members"]:
            if not m.get("email"):
                print(f"  Einladung uebersprungen (keine E-Mail): {m.get('alias')}")
                continue
            client.invite_member(board["id"], m["email"], m.get("name"))
            print(f"  Eingeladen:     {m.get('name') or m['alias']} <{m['email']}>")

    print(f"\nFertig. Board: {board['url']}")
    return 0


def cmd_members(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    joined = client.board_members(board["id"])
    print(f"Mitglieder im Board {board['name']!r}:")
    for bm in joined:
        print(f"  - {bm.get('fullName')} (@{bm.get('username')})")
    print("\nZuordnung team.json -> Trello:")
    for m in cfg["members"]:
        mid = resolve_member_id(client, board["id"], cfg, m["alias"])
        state = "verknuepft" if mid else "NICHT im Board (Einladung offen?)"
        print(f"  {m['alias']:<12} {m.get('name') or '':<22} {state}")
    return 0


def cmd_invite(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    client.invite_member(board["id"], args.email, args.name)
    print(f"Einladung an {args.email} verschickt.")
    return 0


def _create_task(client: TrelloClient, board: dict, cfg: dict, task: dict) -> dict:
    name = (task.get("titel") or task.get("name") or "").strip()
    if not name:
        raise TrelloError(f"Aufgabe ohne Titel: {task!r}")

    assignee = task.get("fuer") or task.get("assignee")
    lst = list_for_task(client, board["id"], cfg, assignee, task.get("liste") or task.get("list"))

    member_ids = []
    warnings = []
    if assignee:
        mid = resolve_member_id(client, board["id"], cfg, assignee)
        if mid:
            member_ids.append(mid)
        else:
            warnings.append(f"{assignee} ist noch nicht im Board - Karte bleibt unzugewiesen")

    label_ids = []
    prio = task.get("prio") or task.get("priority")
    if prio:
        color = cfg["priorities"].get(prio.casefold())
        if not color:
            warnings.append(f"Prioritaet {prio!r} nicht in team.json definiert")
        else:
            label_ids.append(client.ensure_label(board["id"], prio.casefold(), color)["id"])

    due = parse_due(task.get("bis") or task.get("due") or "")

    card = client.create_card(
        lst["id"], name,
        desc=task.get("notiz") or task.get("desc"),
        due=due,
        member_ids=member_ids,
        label_ids=label_ids,
    )

    items = task.get("schritte") or task.get("checklist") or []
    if items:
        client.add_checklist(card["id"], "Schritte", items)

    card["_list"] = lst["name"]
    card["_warnings"] = warnings
    return card


def cmd_add(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    task = {
        "titel": args.titel,
        "fuer": args.fuer,
        "bis": args.bis,
        "liste": args.liste,
        "notiz": args.notiz,
        "prio": args.prio,
        "schritte": args.schritt or [],
    }
    card = _create_task(client, board, cfg, task)
    due = f", faellig {card['due'][:16].replace('T', ' ')}" if card.get("due") else ""
    print(f"Angelegt in {card['_list']!r}: {card['name']}{due}")
    print(f"  {card['shortUrl']}")
    for w in card["_warnings"]:
        print(f"  Hinweis: {w}")
    return 0


def cmd_bulk(client: TrelloClient, cfg: dict, args) -> int:
    raw = sys.stdin.read() if args.datei == "-" else Path(args.datei).read_text(encoding="utf-8")
    data = json.loads(raw)
    tasks = data.get("aufgaben") or data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(tasks, list):
        raise TrelloError("Erwartet wird eine JSON-Liste oder {\"aufgaben\": [...]}.")

    board = resolve_board(client, cfg)
    failures = 0
    for task in tasks:
        try:
            card = _create_task(client, board, cfg, task)
        except (TrelloError, DateParseError) as exc:
            failures += 1
            print(f"FEHLER bei {task.get('titel') or task!r}: {exc}", file=sys.stderr)
            continue
        due = f" (bis {card['due'][:10]})" if card.get("due") else ""
        print(f"+ [{card['_list']}] {card['name']}{due}")
        for w in card["_warnings"]:
            print(f"    Hinweis: {w}")

    print(f"\n{len(tasks) - failures} von {len(tasks)} Aufgaben angelegt.")
    print(f"Board: {board['url']}")
    return 1 if failures else 0


def cmd_show(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    lists = {l["id"]: l["name"] for l in client.board_lists(board["id"])}
    members = {m["id"]: m.get("fullName") or m.get("username")
               for m in client.board_members(board["id"])}

    filter_id = None
    if args.fuer:
        filter_id = resolve_member_id(client, board["id"], cfg, args.fuer)
        if not filter_id:
            raise TrelloError(f"{args.fuer!r} ist nicht im Board - nichts zu filtern.")

    cards = client.board_cards(board["id"])
    by_list: dict[str, list[dict]] = {name: [] for name in lists.values()}
    for card in cards:
        if filter_id and filter_id not in card.get("idMembers", []):
            continue
        if args.offen and (card.get("dueComplete")
                           or lists.get(card["idList"], "").casefold()
                           == cfg["done_list"].casefold()):
            continue
        by_list.setdefault(lists.get(card["idList"], "?"), []).append(card)

    print(f"Board {board['name']!r}  {board['url']}\n")
    for name, items in by_list.items():
        if not items and args.offen:
            continue
        print(f"## {name}  ({len(items)})")
        for card in sorted(items, key=lambda c: c.get("due") or "9999"):
            parts = []
            if card.get("due"):
                parts.append("bis " + card["due"][:10])
            who = [members.get(i, "?") for i in card.get("idMembers", [])]
            if who:
                parts.append(", ".join(who))
            if card.get("dueComplete"):
                parts.append("erledigt")
            suffix = f"  [{' | '.join(parts)}]" if parts else ""
            print(f"  - {card['name']}{suffix}")
        print()
    return 0


def _find_card(client: TrelloClient, board_id: str, query: str) -> dict:
    cards = client.board_cards(board_id)
    exact = [c for c in cards if c["name"].casefold() == query.casefold()]
    hits = exact or [c for c in cards if query.casefold() in c["name"].casefold()]
    if not hits:
        raise TrelloError(f"Keine Karte gefunden fuer {query!r}.")
    if len(hits) > 1:
        names = "\n  ".join(c["name"] for c in hits)
        raise TrelloError(f"{query!r} passt auf mehrere Karten:\n  {names}")
    return hits[0]


def cmd_move(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    card = _find_card(client, board["id"], args.karte)
    lst = find_list(client, board["id"], args.liste)
    client.update_card(card["id"], idList=lst["id"])
    print(f"{card['name']!r} verschoben nach {lst['name']!r}.")
    return 0


def cmd_assign(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    card = _find_card(client, board["id"], args.karte)
    mid = resolve_member_id(client, board["id"], cfg, args.fuer)
    if not mid:
        raise TrelloError(f"{args.fuer!r} ist noch nicht im Board.")
    client.update_card(card["id"], idMembers=[mid])
    if cfg["layout"] == "members":
        entry = member_entry(cfg, args.fuer)
        lst = find_list(client, board["id"], entry.get("name") or entry["alias"])
        client.update_card(card["id"], idList=lst["id"])
        print(f"{card['name']!r} -> {args.fuer} (Liste {lst['name']!r}).")
    else:
        print(f"{card['name']!r} -> {args.fuer}.")
    return 0


def cmd_done(client: TrelloClient, cfg: dict, args) -> int:
    board = resolve_board(client, cfg)
    card = _find_card(client, board["id"], args.karte)
    fields = {"dueComplete": True} if card.get("due") else {}
    try:
        lst = find_list(client, board["id"], cfg["done_list"])
        fields["idList"] = lst["id"]
    except TrelloError:
        pass  # Keine Erledigt-Liste konfiguriert: nur abhaken.
    if fields:
        client.update_card(card["id"], **fields)
    print(f"{card['name']!r} als erledigt markiert.")
    return 0


# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="trello_cli", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", default=str(DEFAULT_CONFIG), help="Pfad zu team.json")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami", help="Account, Workspaces und Boards anzeigen").set_defaults(fn=cmd_whoami)

    s = sub.add_parser("setup", help="Board, Listen und Labels anlegen (idempotent)")
    s.add_argument("--workspace", help="Workspace fuer ein neues Board")
    s.add_argument("--invite", action="store_true", help="Mitglieder aus team.json einladen")
    s.set_defaults(fn=cmd_setup)

    sub.add_parser("members", help="Mitglieder und ihre Verknuepfung pruefen").set_defaults(fn=cmd_members)

    s = sub.add_parser("invite", help="Person per E-Mail einladen")
    s.add_argument("email")
    s.add_argument("--name")
    s.set_defaults(fn=cmd_invite)

    s = sub.add_parser("add", help="Eine Aufgabe anlegen")
    s.add_argument("titel")
    s.add_argument("--fuer", help="Alias aus team.json")
    s.add_argument("--bis", help="z.B. freitag, morgen, 25.12., 2026-12-25T14:00")
    s.add_argument("--liste", help="Liste explizit waehlen")
    s.add_argument("--notiz", help="Beschreibung der Karte")
    s.add_argument("--prio", help="Prioritaet aus team.json, z.B. hoch")
    s.add_argument("--schritt", action="append", help="Checklisten-Punkt (mehrfach moeglich)")
    s.set_defaults(fn=cmd_add)

    s = sub.add_parser("bulk", help="Mehrere Aufgaben aus JSON anlegen")
    s.add_argument("datei", help="JSON-Datei oder '-' fuer stdin")
    s.set_defaults(fn=cmd_bulk)

    s = sub.add_parser("show", help="Board anzeigen")
    s.add_argument("--fuer", help="Nur Aufgaben einer Person")
    s.add_argument("--offen", action="store_true", help="Erledigte ausblenden")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("move", help="Karte in eine andere Liste schieben")
    s.add_argument("karte")
    s.add_argument("liste")
    s.set_defaults(fn=cmd_move)

    s = sub.add_parser("assign", help="Karte einer Person zuweisen")
    s.add_argument("karte")
    s.add_argument("fuer")
    s.set_defaults(fn=cmd_assign)

    s = sub.add_parser("done", help="Karte als erledigt markieren")
    s.add_argument("karte")
    s.set_defaults(fn=cmd_done)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        client = TrelloClient()
        cfg = load_config(Path(args.config)) if args.cmd != "whoami" else {}
        return args.fn(client, cfg, args)
    except (TrelloError, DateParseError) as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"Fehler: JSON konnte nicht gelesen werden: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
