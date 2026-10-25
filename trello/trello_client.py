"""Schlanker Trello-REST-Client (nur Standardbibliothek).

Auth laeuft ueber API-Key + Token, die als Query-Parameter an jeden Request
angehaengt werden. Beides kommt aus der Umgebung (TRELLO_API_KEY / TRELLO_TOKEN)
oder einer .env-Datei im Projektverzeichnis.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_BASE = "https://api.trello.com/1"

# Trello akzeptiert nur diese Label-Farben.
LABEL_COLORS = [
    "green", "yellow", "orange", "red", "purple",
    "blue", "sky", "lime", "pink", "black",
]


class TrelloError(RuntimeError):
    """Fehler aus der Trello-API oder der lokalen Konfiguration."""


def load_dotenv(path: Path | None = None) -> None:
    """Liest KEY=VALUE-Zeilen aus .env, ohne bestehende Variablen zu ueberschreiben."""
    path = path or Path(__file__).resolve().parent.parent / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


class TrelloClient:
    def __init__(self, key: str | None = None, token: str | None = None):
        load_dotenv()
        self.key = key or os.environ.get("TRELLO_API_KEY", "")
        self.token = token or os.environ.get("TRELLO_TOKEN", "")
        if not self.key or not self.token:
            raise TrelloError(
                "TRELLO_API_KEY und TRELLO_TOKEN fehlen. Siehe trello/README.md "
                "-> Abschnitt 'Zugangsdaten besorgen'."
            )

    # ---------------- HTTP ----------------

    def _request(self, method: str, path: str, params: dict | None = None):
        query = {"key": self.key, "token": self.token}
        for name, value in (params or {}).items():
            if value is None:
                continue
            if isinstance(value, bool):
                value = "true" if value else "false"
            elif isinstance(value, (list, tuple)):
                value = ",".join(str(v) for v in value)
            query[name] = str(value)

        url = f"{API_BASE}{path}?{urllib.parse.urlencode(query)}"
        req = urllib.request.Request(url, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace").strip()
            if exc.code == 401:
                detail += " (Key/Token ungueltig oder Token hat keine Schreibrechte?)"
            raise TrelloError(f"{method} {path} -> HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise TrelloError(f"{method} {path} -> Netzwerkfehler: {exc.reason}") from exc

        if not body:
            return None
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    def get(self, path, **params):
        return self._request("GET", path, params)

    def post(self, path, **params):
        return self._request("POST", path, params)

    def put(self, path, **params):
        return self._request("PUT", path, params)

    def delete(self, path, **params):
        return self._request("DELETE", path, params)

    # ---------------- Account ----------------

    def whoami(self) -> dict:
        return self.get("/members/me", fields="id,username,fullName,email")

    def my_boards(self) -> list[dict]:
        return self.get("/members/me/boards", fields="id,name,url,closed", filter="open")

    def my_organizations(self) -> list[dict]:
        return self.get("/members/me/organizations", fields="id,displayName,name")

    # ---------------- Boards ----------------

    def find_board(self, name: str) -> dict | None:
        wanted = name.strip().casefold()
        for board in self.my_boards():
            if board["name"].strip().casefold() == wanted:
                return board
        return None

    def create_board(self, name: str, org_id: str | None = None) -> dict:
        # defaultLists=false: Trello legt sonst To Do / Doing / Done selbst an.
        return self.post(
            "/boards/",
            name=name,
            defaultLists=False,
            idOrganization=org_id,
            prefs_permissionLevel="private",
        )

    def board_lists(self, board_id: str) -> list[dict]:
        return self.get(f"/boards/{board_id}/lists", fields="id,name,pos,closed")

    def board_members(self, board_id: str) -> list[dict]:
        return self.get(f"/boards/{board_id}/members", fields="id,username,fullName")

    def board_labels(self, board_id: str) -> list[dict]:
        return self.get(f"/boards/{board_id}/labels", fields="id,name,color")

    def board_cards(self, board_id: str) -> list[dict]:
        return self.get(
            f"/boards/{board_id}/cards",
            fields="id,name,desc,due,dueComplete,idList,idMembers,idLabels,shortUrl",
        )

    # ---------------- Listen / Labels ----------------

    def create_list(self, board_id: str, name: str, pos: str | float = "bottom") -> dict:
        return self.post("/lists", name=name, idBoard=board_id, pos=pos)

    def ensure_list(self, board_id: str, name: str, pos: str | float = "bottom") -> dict:
        wanted = name.strip().casefold()
        for lst in self.board_lists(board_id):
            if lst["name"].strip().casefold() == wanted:
                return lst
        return self.create_list(board_id, name, pos)

    def create_label(self, board_id: str, name: str, color: str) -> dict:
        return self.post("/labels", name=name, color=color, idBoard=board_id)

    def ensure_label(self, board_id: str, name: str, color: str) -> dict:
        wanted = name.strip().casefold()
        for label in self.board_labels(board_id):
            if (label.get("name") or "").strip().casefold() == wanted:
                return label
        return self.create_label(board_id, name, color)

    # ---------------- Mitglieder ----------------

    def invite_member(self, board_id: str, email: str, full_name: str | None = None) -> dict:
        return self.put(
            f"/boards/{board_id}/members",
            email=email,
            fullName=full_name,
            type="normal",
        )

    # ---------------- Karten ----------------

    def create_card(
        self,
        list_id: str,
        name: str,
        desc: str | None = None,
        due: str | None = None,
        member_ids: list[str] | None = None,
        label_ids: list[str] | None = None,
        pos: str | float = "bottom",
    ) -> dict:
        return self.post(
            "/cards",
            idList=list_id,
            name=name,
            desc=desc,
            due=due,
            idMembers=member_ids or None,
            idLabels=label_ids or None,
            pos=pos,
        )

    def update_card(self, card_id: str, **fields) -> dict:
        return self.put(f"/cards/{card_id}", **fields)

    def add_checklist(self, card_id: str, name: str, items: list[str]) -> dict:
        checklist = self.post("/checklists", idCard=card_id, name=name)
        for item in items:
            self.post(f"/checklists/{checklist['id']}/checkItems", name=item, checked=False)
        return checklist

    def add_comment(self, card_id: str, text: str) -> dict:
        return self.post(f"/cards/{card_id}/actions/comments", text=text)
