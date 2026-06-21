from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AgentCommand(BaseModel):
    intent: Literal[
        "ocr",
        "gmail_organize",
        "gmail_reply",
        "daily_brief",
        "calendar_read",
        "help",
        "unknown",
    ]
    file_query: Optional[str] = None
    page_start: Optional[int] = Field(default=None, ge=1)
    page_end: Optional[int] = Field(default=None, ge=1)
    email_query: Optional[str] = None
    requested_action: Optional[str] = None
    date_start: Optional[str] = None
    date_end: Optional[str] = None


class EmailDecision(BaseModel):
    category: Literal["important", "schedule", "promotional", "other"]
    summary: str
    safe_to_trash: bool = False
    reason: str


class ReplyDraft(BaseModel):
    body: str
