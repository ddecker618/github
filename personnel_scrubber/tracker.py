"""SQLite tracker for personnel data removal workflow state."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS removals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,
    listing_url TEXT,
    listing_found INTEGER NOT NULL DEFAULT 0,
    removal_submitted INTEGER NOT NULL DEFAULT 0,
    awaiting_email_click INTEGER NOT NULL DEFAULT 0,
    verified INTEGER NOT NULL DEFAULT 0,
    recheck_date TEXT,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_removals_domain ON removals(domain);
CREATE INDEX IF NOT EXISTS idx_removals_verified ON removals(verified);
"""


@dataclass(frozen=True)
class RemovalRecord:
    domain: str
    listing_url: str = ""
    listing_found: bool = False
    removal_submitted: bool = False
    awaiting_email_click: bool = False
    verified: bool = False
    recheck_date: date | None = None
    notes: str = ""


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.commit()


def insert_removal(conn: sqlite3.Connection, record: RemovalRecord) -> int:
    cur = conn.execute(
        """
        INSERT INTO removals (
            domain,
            listing_url,
            listing_found,
            removal_submitted,
            awaiting_email_click,
            verified,
            recheck_date,
            notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.domain,
            record.listing_url,
            int(record.listing_found),
            int(record.removal_submitted),
            int(record.awaiting_email_click),
            int(record.verified),
            record.recheck_date.isoformat() if record.recheck_date else None,
            record.notes,
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_removals(conn: sqlite3.Connection) -> Iterable[sqlite3.Row]:
    return conn.execute(
        """
        SELECT id, domain, listing_url, listing_found, removal_submitted,
               awaiting_email_click, verified, recheck_date, notes,
               created_at, updated_at
        FROM removals
        ORDER BY verified ASC, domain ASC
        """
    ).fetchall()
