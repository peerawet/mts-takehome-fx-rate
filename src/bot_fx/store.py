import sqlite3
from contextlib import closing
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


def save(db_path: Path, rates: list[Rate], fetched_at: str) -> int:
    """Upsert rates and return the total number of rows in the table."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path)) as conn:
        with conn:
            conn.execute(SCHEMA)
            conn.executemany(UPSERT, [(r.period, r.rate, fetched_at) for r in rates])
        return conn.execute("SELECT COUNT(*) FROM rates").fetchone()[0]
