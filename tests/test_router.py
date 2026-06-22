from agent.router import CommandRouter


def test_deterministic_ocr_route_and_range():
    command = CommandRouter._deterministic_parse(
        "OCR pages 2-4 of modern control systems PDF"
    )
    assert command.intent == "ocr"
    assert command.page_start == 2
    assert command.page_end == 4
    assert "modern control systems" in command.file_query


def test_filename_numbers_are_not_treated_as_page_range():
    command = CommandRouter._deterministic_parse(
        "OCR 11-1_Convolution & Transfer function.pdf"
    )
    assert command.intent == "ocr"
    assert command.page_start is None
    assert command.page_end is None
    assert "11-1" in command.file_query


def test_help_route():
    assert CommandRouter._deterministic_parse("help").intent == "help"


def test_gmail_and_daily_brief_routes():
    assert (
        CommandRouter._deterministic_parse("Organize my emails").intent
        == "gmail_organize"
    )
    assert (
        CommandRouter._deterministic_parse("Create my daily briefing").intent
        == "daily_brief"
    )


def test_reply_route_extracts_sender_without_date_range():
    command = CommandRouter._deterministic_parse(
        "Draft a reply to the email from Coursera from 2026-06-11 to 2026-06-12"
    )
    assert command.intent == "gmail_reply"
    assert command.email_query == "Coursera"
