#!/usr/bin/env python3
"""Tests ohne Netzwerkzugriff: Datumsparser und Konfigurationslogik.

    python3 trello/test_trello.py
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dates import DateParseError, parse_due
from trello_cli import load_config, member_entry, target_lists
from trello_client import TrelloError

# Referenztag: Sonntag, 25.10.2026 ... tatsaechlich ein Sonntag? -> unten geprueft.
TODAY = date(2026, 10, 25)


class TestParseDue(unittest.TestCase):
    def test_reference_day_is_sunday(self):
        self.assertEqual(TODAY.weekday(), 6)

    def test_empty(self):
        self.assertIsNone(parse_due("", TODAY))
        self.assertIsNone(parse_due(None, TODAY))

    def test_relative(self):
        self.assertTrue(parse_due("heute", TODAY).startswith("2026-10-25T17:00"))
        self.assertTrue(parse_due("morgen", TODAY).startswith("2026-10-26T17:00"))
        self.assertTrue(parse_due("uebermorgen", TODAY).startswith("2026-10-27"))
        self.assertTrue(parse_due("übermorgen", TODAY).startswith("2026-10-27"))
        self.assertTrue(parse_due("in 3 tagen", TODAY).startswith("2026-10-28"))
        self.assertTrue(parse_due("in 2 wochen", TODAY).startswith("2026-11-08"))

    def test_bis_prefix_is_stripped(self):
        self.assertEqual(parse_due("bis morgen", TODAY), parse_due("morgen", TODAY))

    def test_weekday_is_next_future_one(self):
        # Sonntag -> Freitag ist der 30.10.
        self.assertTrue(parse_due("freitag", TODAY).startswith("2026-10-30"))
        self.assertTrue(parse_due("fr", TODAY).startswith("2026-10-30"))
        # Derselbe Wochentag bedeutet eine Woche spaeter, nicht heute.
        self.assertTrue(parse_due("sonntag", TODAY).startswith("2026-11-01"))

    def test_clock_time(self):
        self.assertTrue(parse_due("freitag 14:00", TODAY).startswith("2026-10-30T14:00"))
        self.assertTrue(parse_due("morgen 9 uhr", TODAY).startswith("2026-10-26T09:00"))
        self.assertTrue(parse_due("morgen 8.30", TODAY).startswith("2026-10-26T08:30"))

    def test_german_date(self):
        self.assertTrue(parse_due("25.12.", TODAY).startswith("2026-12-25"))
        self.assertTrue(parse_due("1.1.2027", TODAY).startswith("2027-01-01"))
        # Datum liegt im laufenden Jahr hinter uns -> naechstes Jahr
        self.assertTrue(parse_due("5.3.", TODAY).startswith("2027-03-05"))

    def test_month_end(self):
        self.assertTrue(parse_due("monatsende", TODAY).startswith("2026-10-31"))

    def test_iso(self):
        self.assertTrue(parse_due("2026-12-24", TODAY).startswith("2026-12-24T17:00"))
        self.assertTrue(parse_due("2026-12-24T08:15", TODAY).startswith("2026-12-24T08:15"))

    def test_invalid(self):
        with self.assertRaises(DateParseError):
            parse_due("irgendwann mal", TODAY)
        with self.assertRaises(DateParseError):
            parse_due("32.13.", TODAY)


BASE_CFG = {
    "board": "Team Board",
    "layout": "members",
    "statuses": ["Backlog", "To Do", "Erledigt"],
    "done_list": "Erledigt",
    "inbox_list": "Backlog",
    "priorities": {"hoch": "red"},
    "members": [
        {"alias": "max", "name": "Max Mustermann", "email": "max@example.com"},
        {"alias": "anna", "name": "Anna Beispiel", "email": "anna@example.com"},
    ],
}


def write_cfg(**overrides) -> Path:
    cfg = {**BASE_CFG, **overrides}
    path = Path(tempfile.mkdtemp()) / "team.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")
    return path


class TestConfig(unittest.TestCase):
    def test_load_and_defaults(self):
        cfg = load_config(write_cfg())
        self.assertEqual(cfg["board"], "Team Board")
        self.assertEqual(cfg["layout"], "members")

    def test_missing_file(self):
        with self.assertRaises(TrelloError):
            load_config(Path("/nonexistent/team.json"))

    def test_board_required(self):
        path = Path(tempfile.mkdtemp()) / "team.json"
        path.write_text(json.dumps({"members": []}), encoding="utf-8")
        with self.assertRaises(TrelloError):
            load_config(path)

    def test_bad_layout(self):
        with self.assertRaises(TrelloError):
            load_config(write_cfg(layout="quatsch"))

    def test_lists_member_layout(self):
        cfg = load_config(write_cfg())
        self.assertEqual(
            target_lists(cfg),
            ["Backlog", "Max Mustermann", "Anna Beispiel", "Erledigt"],
        )

    def test_lists_status_layout(self):
        cfg = load_config(write_cfg(layout="status"))
        self.assertEqual(target_lists(cfg), ["Backlog", "To Do", "Erledigt"])

    def test_lists_no_duplicates(self):
        cfg = load_config(write_cfg(
            members=[{"alias": "backlog", "name": "Backlog"}]))
        self.assertEqual(target_lists(cfg), ["Backlog", "Erledigt"])


class TestMemberLookup(unittest.TestCase):
    def setUp(self):
        self.cfg = load_config(write_cfg())

    def test_by_alias(self):
        self.assertEqual(member_entry(self.cfg, "max")["name"], "Max Mustermann")

    def test_case_insensitive(self):
        self.assertEqual(member_entry(self.cfg, "MAX")["alias"], "max")

    def test_by_full_name(self):
        self.assertEqual(member_entry(self.cfg, "Anna Beispiel")["alias"], "anna")

    def test_by_first_name(self):
        self.assertEqual(member_entry(self.cfg, "anna")["alias"], "anna")

    def test_by_email(self):
        self.assertEqual(member_entry(self.cfg, "max@example.com")["alias"], "max")

    def test_unknown(self):
        with self.assertRaises(TrelloError):
            member_entry(self.cfg, "nobody")


if __name__ == "__main__":
    unittest.main(verbosity=2)
