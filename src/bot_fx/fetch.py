from datetime import date, datetime, timedelta, timezone

import httpx

BASE_URL = "https://gateway.api.bot.or.th/Stat-ReferenceRate/v2/DAILY_REF_RATE/"

# The API rejects any request where end_period - start_period > 31 days (HTTP 400).
MAX_SPAN_DAYS = 31
WINDOW_COUNT = 2
TIMEOUT_SECONDS = 30.0

# Thailand has no daylight saving, so a fixed offset is exact and needs no tzdata.
BANGKOK = timezone(timedelta(hours=7), name="Asia/Bangkok")


class ApiError(Exception):
    pass


def now_bangkok() -> datetime:
    return datetime.now(BANGKOK)


def date_windows(end: date, count: int = WINDOW_COUNT, span_days: int = MAX_SPAN_DAYS) -> list[tuple[date, date]]:
    """Back-to-back (start, end) windows ending at `end`, newest first."""
    windows = []
    for _ in range(count):
        start = end - timedelta(days=span_days)
        windows.append((start, end))
        end = start - timedelta(days=1)
    return windows


def fetch_window(client: httpx.Client, api_key: str, start: date, end: date) -> list[dict]:
    response = client.get(
        BASE_URL,
        params={"start_period": start.isoformat(), "end_period": end.isoformat()},
        headers={"Authorization": api_key, "accept": "application/json"},
    )

    status = response.status_code
    body = response.text[:300]
    if status == 401:
        raise ApiError(f"401 Unauthorized: the API did not receive a token. Check BOT_API_KEY. Response: {body}")
    if status == 403:
        raise ApiError(
            "403 Forbidden: the token was rejected. Check that BOT_API_KEY is copied in full "
            f"and that your app's subscription is approved on the portal. Response: {body}"
        )
    if status != 200:
        raise ApiError(f"HTTP {status} for {start}..{end}. Response: {body}")

    try:
        rows = response.json()["result"]["data"]["data_detail"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ApiError(f"Unexpected response shape for {start}..{end}: {body}") from exc
    if not isinstance(rows, list):
        raise ApiError(f"Expected data_detail to be a list for {start}..{end}, got {type(rows).__name__}")
    return rows
