import logging
import sqlite3
from datetime import datetime

import httpx

from bot_fx.cli import run
from bot_fx.config import Settings
from bot_fx.fetch import BANGKOK

NOW = datetime(2026, 11, 26, 21, 20, tzinfo=BANGKOK)


def fake_api(newest_window: dict, older_window: dict) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params["end_period"] == "2026-11-26":
            return httpx.Response(200, json=newest_window)
        return httpx.Response(200, json=older_window)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_saves_twenty_latest_business_days(tmp_path, month_response, empty_response):
    settings = Settings(api_key="secret-token", db_path=tmp_path / "rates.db")

    saved = run(settings, fake_api(month_response, empty_response), NOW)

    assert saved == 20
    with sqlite3.connect(settings.db_path) as conn:
        periods = [p for (p,) in conn.execute("SELECT period FROM rates ORDER BY period")]
    assert len(periods) == 20
    assert periods[-1] == "2026-11-26"


def test_second_run_keeps_twenty_rows(tmp_path, month_response, empty_response):
    settings = Settings(api_key="secret-token", db_path=tmp_path / "rates.db")

    run(settings, fake_api(month_response, empty_response), NOW)
    run(settings, fake_api(month_response, empty_response), NOW)

    with sqlite3.connect(settings.db_path) as conn:
        assert conn.execute("SELECT COUNT(*) FROM rates").fetchone()[0] == 20


def test_warns_when_fewer_than_twenty_days(tmp_path, empty_response, month_response, caplog):
    month_response["result"]["data"]["data_detail"] = month_response["result"]["data"]["data_detail"][:5]
    settings = Settings(api_key="secret-token", db_path=tmp_path / "rates.db")

    with caplog.at_level(logging.WARNING, logger="bot_fx"):
        saved = run(settings, fake_api(month_response, empty_response), NOW)

    assert saved == 5
    assert "Got 5 business days, expected 20" in caplog.text
