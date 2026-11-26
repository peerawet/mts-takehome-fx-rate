import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DB_FILENAME = "bot_api_daily_peerawet.db"


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    api_key: str
    db_path: Path


def default_db_path() -> Path:
    # The brief wants the file inside the project's .venv. Under `uv run`,
    # sys.prefix *is* that .venv, whatever the current directory is.
    if sys.prefix != sys.base_prefix:
        return Path(sys.prefix) / DB_FILENAME
    return Path(".venv") / DB_FILENAME


def load_settings() -> Settings:
    load_dotenv()  # values already in the environment win over .env

    api_key = os.environ.get("BOT_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "BOT_API_KEY is not set. Copy .env.example to .env and paste your token "
            "from portal.api.bot.or.th (Profile -> My apps -> Copy token)."
        )

    db_path = os.environ.get("BOT_DB_PATH", "").strip()
    return Settings(
        api_key=api_key,
        db_path=Path(db_path) if db_path else default_db_path(),
    )
