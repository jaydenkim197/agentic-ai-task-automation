from agent.models import EmailDecision
from tools.gmail_tool import GmailReview, GmailTool


def test_protected_email_is_never_trashed():
    message = {
        "from": "Security <security@example.com>",
        "subject": "Password verification required",
        "body": "Verify your account.",
    }
    decision = EmailDecision(
        category="promotional",
        summary="Promotional-looking message.",
        safe_to_trash=True,
        reason="Model decision",
    )
    assert not GmailTool._can_trash(message, decision)


def test_promotional_email_can_be_trashed():
    message = {
        "from": "Deals <offers@example.com>",
        "subject": "Weekend sale",
        "body": "Save 30 percent on selected products.",
    }
    decision = EmailDecision(
        category="promotional",
        summary="Retail sale promotion.",
        safe_to_trash=True,
        reason="Unmistakable promotion",
    )
    assert GmailTool._can_trash(message, decision)


def test_email_report_lists_trash_action():
    message = {
        "id": "m1",
        "from": "Deals <offers@example.com>",
        "subject": "Weekend sale",
        "body": "Sale",
    }
    decision = EmailDecision(
        category="promotional",
        summary="Retail sale promotion.",
        safe_to_trash=True,
        reason="Unmistakable promotion",
    )
    report = GmailTool.render_report(
        GmailReview(decisions=[(message, decision)], trashed=[message]),
        "2026-06-20T23:50+09:00",
        "2026-06-19 to 2026-06-20",
    )
    assert "Moved to Trash: 1" in report
    assert "Weekend sale" in report
