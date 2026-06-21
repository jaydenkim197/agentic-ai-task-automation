from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from googleapiclient.discovery import build

from tools.google_auth import get_google_credentials


CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


class CalendarTool:
    def __init__(
        self,
        credentials_file: Path,
        token_file: Path,
        timezone_name: str,
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.timezone = ZoneInfo(timezone_name)
        self._service = None

    @property
    def service(self):
        if self._service is None:
            credentials = get_google_credentials(
                CALENDAR_SCOPES, self.credentials_file, self.token_file
            )
            self._service = build("calendar", "v3", credentials=credentials)
        return self._service

    def upcoming(self, hours: int = 48) -> list[dict]:
        now = datetime.now(self.timezone)
        end = now + timedelta(hours=hours)
        result = (
            self.service.events()
            .list(
                calendarId="primary",
                timeMin=now.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
                orderBy="startTime",
                maxResults=50,
            )
            .execute()
        )
        return result.get("items", [])

