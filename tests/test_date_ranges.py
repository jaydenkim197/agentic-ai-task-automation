from datetime import timedelta

import pytest

from agent.date_ranges import parse_date_range


def test_relative_hour_range():
    result = parse_date_range("Organize my emails from the last 48 hours", "Asia/Seoul")
    assert result is not None
    assert result.label == "Last 48 hours"
    assert timedelta(hours=47, minutes=59) < result.end - result.start


def test_absolute_date_range_includes_full_end_day():
    result = parse_date_range("2026-06-01 to 2026-06-20", "Asia/Seoul")
    assert result is not None
    assert result.label == "2026-06-01 to 2026-06-20"
    assert result.start.day == 1
    assert result.end.day == 21


def test_korean_absolute_date_range():
    result = parse_date_range("2026년 6월 1일~2026년 6월 20일", "Asia/Seoul")
    assert result is not None
    assert result.label == "2026-06-01 to 2026-06-20"


def test_missing_range_returns_none():
    assert parse_date_range("Organize my emails", "Asia/Seoul") is None


def test_reversed_range_is_rejected():
    with pytest.raises(ValueError):
        parse_date_range("2026-06-20 to 2026-06-01", "Asia/Seoul")
