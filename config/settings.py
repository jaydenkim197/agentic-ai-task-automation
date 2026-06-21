from __future__ import annotations

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    discord_bot_token: str
    discord_allowed_user_id: int
    openai_api_key: str

    onedrive_root: Path = (
        Path.home() / "Library/CloudStorage/OneDrive-Personal/PROJECT_FOLDER"
    )
    openai_router_model: str = "gpt-5.4-mini"
    openai_ocr_model: str = "gpt-5.4-mini"
    openai_summary_model: str = "gpt-5.4-mini"

    ocr_max_pages_per_run: int = Field(default=20, ge=1, le=100)
    ocr_render_dpi: int = Field(default=160, ge=96, le=240)
    ocr_max_candidates: int = Field(default=5, ge=1, le=10)
    ocr_search_max_depth: int = Field(default=4, ge=1, le=10)

    google_credentials_file: Path = Path("credentials.json")
    google_token_file: Path = Path("token.json")
    google_sheet_id: str
    google_study_sheet: str = "공부일정"
    google_project_sheet: str = "프로젝트일정"
    app_timezone: str = "Asia/Seoul"
    report_directory: Path = Path("storage")

    @field_validator("onedrive_root")
    @classmethod
    def normalize_root(cls, value: Path) -> Path:
        root = value.expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"ONEDRIVE_ROOT does not exist: {root}")
        return root


def load_settings() -> Settings:
    return Settings()
