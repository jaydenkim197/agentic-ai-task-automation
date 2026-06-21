from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


ALL_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_google_credentials(
    scopes: list[str] | None, credentials_file: Path, token_file: Path
) -> Credentials:
    requested_scopes = ALL_GOOGLE_SCOPES
    credentials = None
    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(
            str(token_file), requested_scopes
        )
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    elif not credentials or not credentials.valid:
        if not credentials_file.exists():
            raise FileNotFoundError(
                f"Google OAuth client file not found: {credentials_file}"
            )
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file), requested_scopes
        )
        credentials = flow.run_local_server(port=0)
    token_file.write_text(credentials.to_json(), encoding="utf-8")
    token_file.chmod(0o600)
    return credentials
