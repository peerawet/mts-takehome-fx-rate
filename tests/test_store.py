import sqlite3

from bot_fx.store import save
from bot_fx.transform import Rate

RATES = [Rate("2026-11-25", 34.025), Rate("2026-11-26", 34.014)]


def test_running_twice_does_not_duplicate_rows(tmp_path):
    db = tmp_path / "rates.db"

    assert save(db, RATES, "2026-11-26T21:00:00+07:00") == 2
    assert save(db, RATES, "2026-11-26T22:00:00+07:00") == 2


def test_upsert_updates_existing_period(tmp_path):
    db = tmp_path / "rates.db"
    save(db, RATES, "2026-11-26T21:00:00+07:00")

    save(db, [Rate("2026-11-26", 34.1)], "2026-11-27T19:00:00+07:00")

    with sqlite3.connect(db) as conn:
        row = conn.execute("SELECT rate, fetched_at FROM rates WHERE period = '2026-11-26'").fetchone()
    assert row == (34.1, "2026-11-27T19:00:00+07:00")


def test_creates_missing_parent_directory(tmp_path):
    db = tmp_path / "nested" / "dir" / "rates.db"

    save(db, RATES, "2026-11-26T21:00:00+07:00")

    assert db.exists()
