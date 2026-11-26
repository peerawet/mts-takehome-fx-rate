import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from .transform import Rate

SCHEMA = """
CREATE TABLE IF NOT EXISTS rates (
    period      TEXT PRIMARY KEY,
    rate        REAL NOT NULL,
    fetched_at  TEXT NOT NULL
)
"""

UPSERT = """
INSERT INTO rates (period, rate, fetched_at) VALUES (?, ?, ?)
ON CONFLICT(period) DO UPDATE SET rate = excluded.rate, fetched_at = excluded.fetched_at
"""


@dataclass(frozen=True)
class Change:
    """A stored rate that the API now reports with a different value."""
    period: str
    old_rate: float
    new_rate: float
    old_fetched_at: str


@dataclass(frozen=True)
class SaveResult:
    total_rows: int
    changes: list[Change]


def _find_changes(conn: sqlite3.Connection, rates: list[Rate]) -> list[Change]:
    stored = {
        period: (rate, fetched_at)
        for period, rate, fetched_at in conn.execute(
            f"SELECT period, rate, fetched_at FROM rates WHERE period IN ({','.join('?' * len(rates))})",
            [r.period for r in rates],
        )
    }
    changes = []
    for r in rates:
        if r.period in stored:
            old_rate, old_fetched_at = stored[r.period]
            # The API publishes 7 decimal places; compare at that precision.
            if round(old_rate, 7) != round(r.rate, 7):
                changes.append(Change(r.period, old_rate, r.rate, old_fetched_at))
    return changes


def save(db_path: Path, rates: list[Rate], fetched_at: str) -> SaveResult:
    """Upsert rates; report rows whose stored value differed from the new one."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(SCHEMA)
            changes = _find_changes(conn, rates) if rates else []
            conn.executemany(UPSERT, [(r.period, r.rate, fetched_at) for r in rates])
        total = conn.execute("SELECT COUNT(*) FROM rates").fetchone()[0]
    return SaveResult(total_rows=total, changes=changes)
