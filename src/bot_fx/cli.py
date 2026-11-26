import logging
from datetime import datetime

import httpx

from .config import ConfigError, Settings, load_settings
from .fetch import TIMEOUT_SECONDS, ApiError, date_windows, fetch_window, now_bangkok
from .store import save
from .transform import latest, parse_rows

TARGET_ROWS = 20

log = logging.getLogger("bot_fx")


def run(settings: Settings, client: httpx.Client, now: datetime) -> int:
    rows = []
    for start, end in date_windows(now.date()):
        log.info("Fetching %s .. %s", start, end)
        rows.extend(fetch_window(client, settings.api_key, start, end))

    rates = latest(parse_rows(rows), TARGET_ROWS)
    if len(rates) < TARGET_ROWS:
        log.warning("Got %d business days, expected %d", len(rates), TARGET_ROWS)
    if not rates:
        return 0

    total = save(settings.db_path, rates, now.isoformat(timespec="seconds"))
    log.info(
        "Saved %d rows (%s .. %s) to %s; table now holds %d rows",
        len(rates), rates[0].period, rates[-1].period, settings.db_path, total,
    )
    return len(rates)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logging.getLogger("httpx").setLevel(logging.WARNING)
    try:
        settings = load_settings()
        with httpx.Client(timeout=TIMEOUT_SECONDS) as client:
            run(settings, client, now_bangkok())
    except (ConfigError, ApiError) as exc:
        log.error("%s", exc)
        return 1
    except httpx.HTTPError as exc:
        log.error("Could not reach the BOT API: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
