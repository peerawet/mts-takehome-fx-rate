import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def month_response() -> dict:
    """Real response for 2026-10-26 .. 2026-11-26: 24 business days, newest first."""
    return load_fixture("daily_ref_rate_2026-10-26_2026-11-26.json")


@pytest.fixture
def empty_response() -> dict:
    """Real response for a range with no business days (weekend, holiday or future)."""
    return load_fixture("daily_ref_rate_no_business_days.json")
