from datetime import date

import httpx
import pytest

from bot_fx.fetch import MAX_SPAN_DAYS, ApiError, date_windows, fetch_window


def client_returning(status: int, body: dict | str, seen: list | None = None) -> httpx.Client:
    def handler(request: httpx.Request) -> httpx.Response:
        if seen is not None:
            seen.append(request)
        if isinstance(body, dict):
            return httpx.Response(status, json=body)
        return httpx.Response(status, text=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_windows_stay_within_api_limit_and_do_not_overlap():
    windows = date_windows(date(2026, 11, 26))

    assert windows[0] == (date(2026, 10, 26), date(2026, 11, 26))
    assert windows[1][1] == date(2026, 10, 25)
    for start, end in windows:
        assert (end - start).days <= MAX_SPAN_DAYS


def test_sends_token_without_bearer_prefix(month_response):
    seen = []
    client = client_returning(200, month_response, seen)

    rows = fetch_window(client, "secret-token", date(2026, 10, 26), date(2026, 11, 26))

    assert len(rows) == 24
    assert seen[0].headers["Authorization"] == "secret-token"
    assert seen[0].url.params["start_period"] == "2026-10-26"
    assert seen[0].url.params["end_period"] == "2026-11-26"


@pytest.mark.parametrize(
    ("status", "body", "expected"),
    [
        (401, {"error": "Authorization field missing"}, "401 Unauthorized"),
        (403, {"error": "Access to this API has been disallowed"}, "403 Forbidden"),
        (
            400,
            {"httpCode": "400", "httpMessage": "Bad Request",
             "moreInformation": [{"message": "Exceed limit period. Limit period is 31 days"}]},
            "Exceed limit period",
        ),
    ],
)
def test_error_statuses_raise_readable_errors(status, body, expected):
    client = client_returning(status, body)

    with pytest.raises(ApiError, match=expected):
        fetch_window(client, "secret-token", date(2026, 10, 1), date(2026, 11, 26))


def test_error_message_never_contains_the_token():
    client = client_returning(403, {"error": "Access to this API has been disallowed"})

    with pytest.raises(ApiError) as excinfo:
        fetch_window(client, "secret-token", date(2026, 10, 26), date(2026, 11, 26))
    assert "secret-token" not in str(excinfo.value)
