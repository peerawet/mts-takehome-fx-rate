from pathlib import Path

import pytest

from bot_fx import config
from bot_fx.config import ConfigError, load_settings


@pytest.fixture(autouse=True)
def no_dotenv(monkeypatch):
    monkeypatch.setattr(config, "load_dotenv", lambda: None)


def test_missing_key_explains_how_to_set_it(monkeypatch):
    monkeypatch.delenv("BOT_API_KEY", raising=False)

    with pytest.raises(ConfigError, match="BOT_API_KEY is not set"):
        load_settings()


def test_db_path_can_be_overridden(monkeypatch, tmp_path):
    monkeypatch.setenv("BOT_API_KEY", "secret-token")
    monkeypatch.setenv("BOT_DB_PATH", str(tmp_path / "custom.db"))

    assert load_settings().db_path == tmp_path / "custom.db"


def test_default_db_path_is_inside_the_venv(monkeypatch):
    monkeypatch.setenv("BOT_API_KEY", "secret-token")
    monkeypatch.delenv("BOT_DB_PATH", raising=False)

    db_path = load_settings().db_path

    assert db_path.name == "bot_api_daily_peerawet.db"
    assert db_path.parent.name == ".venv"
