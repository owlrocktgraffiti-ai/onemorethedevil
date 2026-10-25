"""Deutsche Datumsangaben in ISO-8601 umrechnen.

Gedacht fuer diktierte Eingaben: "freitag", "morgen", "in 3 tagen",
"25.12.", "25.12.2026 14:00" oder direkt ISO.
"""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta

WEEKDAYS = {
    "montag": 0, "mo": 0,
    "dienstag": 1, "di": 1,
    "mittwoch": 2, "mi": 2,
    "donnerstag": 3, "do": 3,
    "freitag": 4, "fr": 4,
    "samstag": 5, "sa": 5, "sonnabend": 5,
    "sonntag": 6, "so": 6,
}

# Faellig standardmaessig um 17:00 Ortszeit, wenn keine Uhrzeit genannt wird.
DEFAULT_TIME = time(17, 0)


class DateParseError(ValueError):
    pass


def _iso(d: date, t: time = DEFAULT_TIME) -> str:
    return datetime.combine(d, t).isoformat()


def parse_due(text: str, today: date | None = None) -> str | None:
    """Gibt einen ISO-Timestamp zurueck, oder None fuer leere Eingabe."""
    if text is None:
        return None
    raw = text.strip()
    if not raw:
        return None

    today = today or date.today()
    s = raw.casefold().replace("bis ", "", 1).strip()

    # Uhrzeit abspalten, z.B. "freitag 14:00"
    clock = DEFAULT_TIME
    m = re.search(r"\b(\d{1,2})[:.](\d{2})\s*(?:uhr)?$", s)
    if m and not re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", s):
        hh, mm = int(m.group(1)), int(m.group(2))
        if hh <= 23 and mm <= 59:
            clock = time(hh, mm)
            s = s[: m.start()].strip()
    else:
        m = re.search(r"\b(\d{1,2})\s*uhr$", s)
        if m and int(m.group(1)) <= 23:
            clock = time(int(m.group(1)), 0)
            s = s[: m.start()].strip()

    if not s:
        return _iso(today, clock)

    # Relative Begriffe
    if s in ("heute",):
        return _iso(today, clock)
    if s in ("morgen",):
        return _iso(today + timedelta(days=1), clock)
    if s in ("uebermorgen", "übermorgen"):
        return _iso(today + timedelta(days=2), clock)
    if s in ("naechste woche", "nächste woche"):
        return _iso(today + timedelta(days=7), clock)
    if s in ("monatsende", "ende des monats"):
        nxt = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        return _iso(nxt - timedelta(days=1), clock)

    m = re.fullmatch(r"in\s+(\d+)\s*(tag|tagen|woche|wochen)", s)
    if m:
        n = int(m.group(1))
        days = n * 7 if m.group(2).startswith("woche") else n
        return _iso(today + timedelta(days=days), clock)

    # Wochentage: immer der naechste kuenftige Termin (heute zaehlt nicht)
    key = s.replace("nächsten ", "").replace("naechsten ", "").replace("am ", "").strip()
    if key in WEEKDAYS:
        delta = (WEEKDAYS[key] - today.weekday()) % 7 or 7
        return _iso(today + timedelta(days=delta), clock)

    # TT.MM. / TT.MM.JJJJ
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})?", s)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        if m.group(3):
            year = int(m.group(3))
            year += 2000 if year < 100 else 0
        else:
            year = today.year
            # Liegt der Tag schon hinter uns, ist das naechste Jahr gemeint.
            if (month, day) < (today.month, today.day):
                year += 1
        try:
            return _iso(date(year, month, day), clock)
        except ValueError as exc:
            raise DateParseError(f"Ungueltiges Datum: {raw!r}") from exc

    # ISO
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError:
        pass
    else:
        if parsed.time() == time(0, 0) and "t" not in raw.casefold():
            parsed = datetime.combine(parsed.date(), clock)
        return parsed.isoformat()

    raise DateParseError(
        f"Datum nicht verstanden: {raw!r}. Erlaubt sind z.B. 'morgen', 'freitag', "
        "'in 3 tagen', '25.12.', '2026-12-25' oder '2026-12-25T14:00'."
    )
