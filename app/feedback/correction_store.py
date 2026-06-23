"""
Feature 4 — Human-in-the-loop correction & feedback store.

When a clinician fixes a mistranscribed or mispronounced term, we store the
correction in a small SQLite database. Stored corrections are used to
post-process future Whisper output (simple confirmed-term replacement) and can
be exported for later model fine-tuning.

`CorrectionStore` methods:
    add_correction(...)            -> inserted row id
    get_corrections_for_term(term) -> list of rows matching original_term
    get_all_corrections()          -> all rows, newest first
    count()                        -> total stored
    apply_corrections(text, ...)   -> text with confirmed corrections applied
    export_corrections()           -> CSV string

Schema:
    id, original_term, corrected_term, context_phrase, timestamp,
    source_language, target_language, user_confirmed
"""

from __future__ import annotations

import os
import re
import io
import csv
import sqlite3
import threading
from datetime import datetime, timezone

_DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "..", "data", "corrections.db")


class CorrectionStore:
    def __init__(self, db_path: str = _DEFAULT_DB):
        self.db_path = os.path.abspath(db_path)
        # SQLite connections aren't shareable across threads by default; a lock
        # keeps the single shared connection safe under Flask's threaded server.
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        with self._lock:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS corrections (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_term   TEXT NOT NULL,
                    corrected_term  TEXT NOT NULL,
                    context_phrase  TEXT,
                    timestamp       TEXT NOT NULL,
                    source_language TEXT,
                    target_language TEXT,
                    user_confirmed  INTEGER NOT NULL DEFAULT 1
                )
                """
            )
            self._conn.commit()

    # ── writes ───────────────────────────────────────────────────────────
    def add_correction(self, original_term, corrected_term, context_phrase="",
                        source_language="", target_language="", user_confirmed=True):
        original_term = (original_term or "").strip()
        corrected_term = (corrected_term or "").strip()
        if not original_term or not corrected_term:
            raise ValueError("original_term and corrected_term are required")

        ts = datetime.now(timezone.utc).isoformat()
        with self._lock:
            cur = self._conn.execute(
                """INSERT INTO corrections
                   (original_term, corrected_term, context_phrase, timestamp,
                    source_language, target_language, user_confirmed)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (original_term, corrected_term, context_phrase, ts,
                 source_language, target_language, 1 if user_confirmed else 0),
            )
            self._conn.commit()
            return cur.lastrowid

    # ── reads ────────────────────────────────────────────────────────────
    def _rows(self, sql, params=()):
        with self._lock:
            return [dict(r) for r in self._conn.execute(sql, params).fetchall()]

    def get_corrections_for_term(self, term: str):
        return self._rows(
            "SELECT * FROM corrections WHERE lower(original_term)=lower(?) "
            "ORDER BY id DESC", (term.strip(),))

    def get_all_corrections(self):
        return self._rows("SELECT * FROM corrections ORDER BY id DESC")

    def count(self) -> int:
        with self._lock:
            return self._conn.execute("SELECT COUNT(*) FROM corrections").fetchone()[0]

    # ── apply confirmed corrections to new transcripts ────────────────────
    def apply_corrections(self, text: str, source_language: str = None) -> str:
        if not text:
            return text
        rows = self.get_all_corrections()
        for r in rows:
            if not r["user_confirmed"]:
                continue
            if source_language and r["source_language"] and \
               r["source_language"].lower() != source_language.lower():
                continue
            pattern = re.compile(r"(?<!\w)" + re.escape(r["original_term"]) + r"(?!\w)",
                                 re.IGNORECASE)
            text = pattern.sub(r["corrected_term"], text)
        return text

    # ── export ───────────────────────────────────────────────────────────
    def export_corrections(self) -> str:
        rows = self.get_all_corrections()
        buf = io.StringIO()
        fields = ["id", "original_term", "corrected_term", "context_phrase",
                  "timestamp", "source_language", "target_language", "user_confirmed"]
        writer = csv.DictWriter(buf, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r.get(k, "") for k in fields})
        return buf.getvalue()


# module-level singleton
correction_store = CorrectionStore()


if __name__ == "__main__":
    import tempfile

    # Use a throwaway DB so the self-check doesn't touch real data.
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    store = CorrectionStore(tmp.name)

    # Test 1: add + retrieve
    rid = store.add_correction("malayria", "malaria",
                               context_phrase="patient has malayria",
                               source_language="en", target_language="es")
    print("1. inserted id", rid, "count", store.count())
    assert rid >= 1 and store.count() == 1

    # Test 2: lookup by term (case-insensitive)
    found = store.get_corrections_for_term("MALAYRIA")
    print("2. found", len(found), found[0]["corrected_term"])
    assert len(found) == 1 and found[0]["corrected_term"] == "malaria"

    # Test 3: apply_corrections rewrites confirmed terms in new text
    fixed = store.apply_corrections("The patient has malayria today.")
    print("3.", fixed)
    assert "malaria" in fixed and "malayria" not in fixed

    # Test 4: CSV export has a header + the row, and bad input is rejected
    csv_out = store.export_corrections()
    assert csv_out.startswith("id,original_term,corrected_term")
    assert "malaria" in csv_out
    try:
        store.add_correction("", "x")
        raised = False
    except ValueError:
        raised = True
    assert raised
    print("4. export length", len(csv_out), "| empty rejected:", raised)

    store._conn.close()   # release the file handle before deleting (Windows)
    try:
        os.unlink(tmp.name)
    except OSError:
        pass
    print("correction_store self-check OK")
