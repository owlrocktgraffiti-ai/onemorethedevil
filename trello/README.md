# Trello-Teamboard

Aufgaben per Sprache/Text diktieren, daraus werden Trello-Karten mit Zuweisung,
Fälligkeit, Priorität und Checkliste. Läuft komplett mit der **kostenlosen
Trello-Version** und ohne externe Python-Pakete (nur Standardbibliothek).

## Was Trello Free hergibt

| | Free |
|---|---|
| Boards | 10 pro Workspace |
| Listen & Karten | unbegrenzt |
| Mitglieder | unbegrenzt einladbar |
| Karten an Personen zuweisen | ja |
| Fälligkeiten, Labels, Checklisten | ja |
| API-Zugriff | ja, kostenlos |

Wichtig: Trello weist Personen **Karten** zu, nicht Listen. Deshalb gibt es hier
zwei Board-Layouts (siehe `layout` unten).

## 1. Zugangsdaten besorgen

1. Auf <https://trello.com/power-ups/admin> einloggen → **New** → Power-Up anlegen
   (Name beliebig, z. B. „Teamboard Automation", Workspace auswählen).
2. Im Power-Up den Reiter **API Key** öffnen → **Generate a new API Key**.
   Das ist der `TRELLO_API_KEY`.
3. Auf derselben Seite rechts auf **Token** („manually generate a Token") klicken
   und den Zugriff bestätigen. Das ist der `TRELLO_TOKEN`.

Dann im Projektverzeichnis:

```bash
cp .env.example .env
# TRELLO_API_KEY und TRELLO_TOKEN eintragen
```

`.env` ist über `.gitignore` ausgeschlossen und landet nicht im Repository.
Alternativ gehen die Werte als Umgebungsvariablen, z. B. als Secret der
Session-Umgebung.

Prüfen:

```bash
python3 trello/trello_cli.py whoami
```

## 2. Team konfigurieren

```bash
cp trello/team.example.json trello/team.json
```

`team.json` ausfüllen:

```json
{
  "board": "Team Board",
  "layout": "members",
  "statuses": ["Backlog", "To Do", "In Arbeit", "Warten auf", "Erledigt"],
  "done_list": "Erledigt",
  "inbox_list": "Backlog",
  "priorities": { "hoch": "red", "mittel": "yellow", "niedrig": "green" },
  "members": [
    { "alias": "max", "name": "Max Mustermann", "email": "max@example.com",
      "trello_username": "" }
  ]
}
```

- **`layout: "members"`** — eine Liste pro Person, dazu `inbox_list` für
  Unverteiltes und `done_list`. Eine Aufgabe mit `--fuer max` landet automatisch
  in der Liste von Max. Gut zu sehen, wer was auf dem Tisch hat.
- **`layout: "status"`** — klassisches Kanban: Listen sind die `statuses`,
  die Person wird als Member auf der Karte gesetzt.
- `alias` ist der Kurzname, den du beim Diktieren benutzt. Erkannt werden auch
  der vollständige Name, der Vorname und die E-Mail-Adresse.
- `trello_username` ist optional, hilft aber beim Zuordnen, wenn der Trello-Name
  von `name` abweicht.

`team.json` steht ebenfalls in `.gitignore`, weil darin E-Mail-Adressen stehen.

## 3. Board anlegen

```bash
python3 trello/trello_cli.py setup --invite
```

Legt Board, Listen und Priority-Labels an und lädt die Mitglieder per E-Mail ein.
Der Befehl ist idempotent: erneut aufrufen schadet nicht, Vorhandenes bleibt
unangetastet. Neue Person später: in `team.json` ergänzen, `setup --invite`
nochmal laufen lassen.

Mitgliedschaften prüfen:

```bash
python3 trello/trello_cli.py members
```

Solange jemand die Einladung nicht angenommen hat, wird die Karte angelegt,
aber nicht zugewiesen — die CLI sagt das in einem Hinweis.

## 4. Aufgaben anlegen

Einzeln:

```bash
python3 trello/trello_cli.py add "Rechnungen Q4 prüfen" \
    --fuer max --bis freitag --prio hoch \
    --notiz "Ordner im Ablagefach" \
    --schritt "Belege sortieren" --schritt "Summen prüfen"
```

Mehrere auf einmal (das ist der Weg für diktierte Listen — ich wandle das
Gesprochene in diese JSON-Struktur um und spiele sie ein):

```bash
python3 trello/trello_cli.py bulk trello/tasks.example.json
# oder über die Pipe:
echo '{"aufgaben":[{"titel":"Angebot Meier","fuer":"anna","bis":"morgen"}]}' \
  | python3 trello/trello_cli.py bulk -
```

Eine fehlerhafte Aufgabe bricht den Rest nicht ab; der Exit-Code ist dann 1 und
die Fehler stehen auf stderr.

### Datumsangaben

`--bis` versteht deutsche Umgangssprache:

| Eingabe | Ergebnis |
|---|---|
| `heute`, `morgen`, `übermorgen` | entsprechender Tag, 17:00 |
| `freitag`, `fr`, `montag` | der nächste künftige Wochentag |
| `in 3 tagen`, `in 2 wochen` | relativ zu heute |
| `monatsende` | letzter Tag des Monats |
| `25.12.`, `1.1.2027` | ohne Jahr: nächstes Vorkommen |
| `2026-12-24T08:15` | ISO direkt |
| `freitag 14:00`, `morgen 9 uhr` | mit Uhrzeit |

Ohne Uhrzeit wird 17:00 Ortszeit angenommen.

## 5. Laufender Betrieb

```bash
python3 trello/trello_cli.py show                  # ganzes Board
python3 trello/trello_cli.py show --fuer max --offen
python3 trello/trello_cli.py assign "Angebot Meier" anna
python3 trello/trello_cli.py move "Angebot Meier" "In Arbeit"
python3 trello/trello_cli.py done "Rechnungen"
```

Karten werden über einen Namensausschnitt gefunden. Passt der Ausschnitt auf
mehrere Karten, bricht der Befehl mit einer Auswahlliste ab, statt die falsche
Karte zu erwischen.

## Tests

```bash
python3 trello/test_trello.py
```

23 Tests für Datumsparser, Konfiguration und Namensauflösung — ohne Netzzugriff
und ohne Zugangsdaten. Die API-Schicht und die CLI-Befehle wurden zusätzlich
gegen einen lokalen Fake-Trello-Server geprüft (34 Prüfungen, alle grün).

## Dateien

| Datei | Zweck |
|---|---|
| `trello_client.py` | REST-Client (stdlib `urllib`), Auth, Fehlerbehandlung |
| `trello_cli.py` | Befehle: setup, add, bulk, show, assign, move, done, members |
| `dates.py` | deutsche Datumsangaben → ISO-8601 |
| `team.example.json` | Vorlage für `team.json` |
| `tasks.example.json` | Vorlage für `bulk` |
| `test_trello.py` | Tests |

## Später: MCP statt CLI

Die CLI reicht für den Alltag. Wer die Trello-Funktionen dauerhaft als Tools in
jeder Session haben will, kann `trello_client.py` unverändert hinter einen
MCP-Server hängen — die Befehle aus `trello_cli.py` entsprechen dann eins zu
eins den Tool-Definitionen. Dafür ist kein Umbau des Clients nötig.
