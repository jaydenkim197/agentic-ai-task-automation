from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class DateRange:
    start: datetime
    end: datetime
    label: str

    def gmail_query(self) -> str:
        return f"after:{int(self.start.timestamp())} before:{int(self.end.timestamp())}"


def parse_date_range(text: str, timezone_name: str) -> DateRange | None:
    timezone = ZoneInfo(timezone_name)
    now = datetime.now(timezone)
    normalized = text.strip().lower()

    relative = re.search(
        r"(?:last|past|최근)\s*(\d+)\s*(hours?|hrs?|시간|days?|일)",
        normalized,
    )
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2)
        if amount < 1 or amount > 365:
            raise ValueError("The date range must be between 1 hour and 365 days.")
        delta = (
            timedelta(hours=amount)
            if unit.startswith(("hour", "hr")) or unit == "시간"
            else timedelta(days=amount)
        )
        label_unit = (
            "hours"
            if unit.startswith(("hour", "hr")) or unit == "시간"
            else "days"
        )
        return DateRange(
            start=now - delta,
            end=now,
            label=f"Last {amount} {label_unit}",
        )

    dates = re.findall(
        r"(?<!\d)(20\d{2})[-/.년]\s*(\d{1,2})[-/.월]\s*(\d{1,2})(?:일)?",
        text,
    )
    if len(dates) >= 2:
        start_date = datetime(
            int(dates[0][0]), int(dates[0][1]), int(dates[0][2]), tzinfo=timezone
        )
        end_date = datetime(
            int(dates[1][0]), int(dates[1][1]), int(dates[1][2]), tzinfo=timezone
        ) + timedelta(days=1)
        if end_date <= start_date:
            raise ValueError("The end date must be on or after the start date.")
        if end_date - start_date > timedelta(days=366):
            raise ValueError("The date range cannot exceed 366 days.")
        return DateRange(
            start=start_date,
            end=end_date,
            label=(
                f"{start_date.date().isoformat()} to "
                f"{(end_date - timedelta(days=1)).date().isoformat()}"
            ),
        )

    return None
