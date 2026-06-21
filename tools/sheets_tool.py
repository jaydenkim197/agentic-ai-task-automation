from __future__ import annotations

from pathlib import Path

from googleapiclient.discovery import build

from tools.google_auth import get_google_credentials


SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


class SheetsTool:
    def __init__(
        self,
        spreadsheet_id: str,
        study_sheet: str,
        project_sheet: str,
        credentials_file: Path,
        token_file: Path,
    ):
        self.spreadsheet_id = spreadsheet_id
        self.study_sheet = study_sheet
        self.project_sheet = project_sheet
        self.credentials_file = credentials_file
        self.token_file = token_file
        self._service = None

    @property
    def service(self):
        if self._service is None:
            credentials = get_google_credentials(
                SHEETS_SCOPES, self.credentials_file, self.token_file
            )
            self._service = build("sheets", "v4", credentials=credentials)
        return self._service

    def read_active_tasks(self) -> list[dict]:
        tasks = []
        tasks.extend(
            self._read_sheet(
                self.study_sheet,
                identity_columns=("과목", "작업"),
                completion_columns=("완료일",),
            )
        )
        tasks.extend(
            self._read_sheet(
                self.project_sheet,
                identity_columns=("프로젝트", "작업내용", "작업"),
                completion_columns=("완료일", "상태"),
            )
        )
        return tasks

    def _read_sheet(
        self,
        sheet_name: str,
        identity_columns: tuple[str, ...],
        completion_columns: tuple[str, ...],
    ) -> list[dict]:
        result = (
            self.service.spreadsheets()
            .values()
            .get(
                spreadsheetId=self.spreadsheet_id,
                range=f"'{sheet_name}'!A1:R500",
                valueRenderOption="FORMATTED_VALUE",
            )
            .execute()
        )
        rows = result.get("values", [])
        if not rows:
            return []
        headers = rows[0]
        output = []
        for row in rows[1:]:
            item = {
                header: row[index] if index < len(row) else ""
                for index, header in enumerate(headers)
                if header
            }
            if not any(item.get(column, "").strip() for column in identity_columns):
                continue
            if self._is_completed(item, completion_columns):
                continue
            item["_sheet"] = sheet_name
            output.append(item)
        return output

    @staticmethod
    def _is_completed(item: dict, completion_columns: tuple[str, ...]) -> bool:
        completed_words = {"완료", "done", "completed", "complete", "✔", "✓"}
        for column in completion_columns:
            value = str(item.get(column, "")).strip().lower()
            if column == "완료일" and value:
                return True
            if value in completed_words:
                return True
        return False

