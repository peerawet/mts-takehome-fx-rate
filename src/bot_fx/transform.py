from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Rate:
    period: str  # 'YYYY-MM-DD'
    rate: float  # THB per 1 USD


def parse_rows(rows: list[dict]) -> list[Rate]:
    rates = []
    for row in rows:
        period = (row.get("period") or "").strip()
        value = (row.get("rate") or "").strip()
        # Days without data (weekends, holidays, future dates) come back as
        # a single {"period": "", "rate": ""} row instead of an empty list.
        if not period or not value:
            continue
        date.fromisoformat(period)
        rates.append(Rate(period=period, rate=float(value)))
    return rates


def latest(rates: list[Rate], count: int) -> list[Rate]:
    """The `count` most recent business days, oldest first, one row per period."""
    by_period = {r.period: r for r in rates}
    return sorted(by_period.values(), key=lambda r: r.period)[-count:]
