from bot_fx.transform import Rate, latest, parse_rows


def test_parses_real_response(month_response):
    rates = parse_rows(month_response["result"]["data"]["data_detail"])

    assert len(rates) == 24
    assert rates[0] == Rate(period="2026-11-26", rate=34.014)
    assert all(isinstance(r.rate, float) for r in rates)


def test_drops_placeholder_row_for_days_without_data(empty_response):
    assert parse_rows(empty_response["result"]["data"]["data_detail"]) == []


def test_latest_sorts_oldest_first_and_keeps_most_recent(month_response):
    rates = latest(parse_rows(month_response["result"]["data"]["data_detail"]), 20)

    assert len(rates) == 20
    assert [r.period for r in rates] == sorted(r.period for r in rates)
    assert rates[-1].period == "2026-11-26"
    assert rates[0].period == "2026-10-30"


def test_latest_removes_duplicate_periods():
    rates = [Rate("2026-11-25", 34.025), Rate("2026-11-26", 34.014), Rate("2026-11-26", 34.014)]

    assert latest(rates, 20) == [Rate("2026-11-25", 34.025), Rate("2026-11-26", 34.014)]
