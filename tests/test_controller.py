from agent.controller import AgentController
from agent.models import AgentCommand


def test_dispatch_asks_for_missing_gmail_range():
    controller = object.__new__(AgentController)
    controller.settings = type("Settings", (), {"app_timezone": "Asia/Seoul"})()
    controller.pending_gmail_organization = None
    response = controller._dispatch(
        AgentCommand(intent="gmail_organize"),
        "Organize my emails",
    )
    assert "Please provide a Gmail date range" in response
    assert controller.pending_gmail_organization is not None


def test_dispatch_parses_gmail_range_without_name_error():
    controller = object.__new__(AgentController)
    controller.settings = type("Settings", (), {"app_timezone": "Asia/Seoul"})()
    captured = {}

    def fake_organize(date_range):
        captured["label"] = date_range.label
        return "organized"

    controller._organize_gmail = fake_organize
    response = controller._dispatch(
        AgentCommand(intent="gmail_organize"),
        "Organize my emails from 2026-06-01 to 2026-06-20",
    )
    assert response == "organized"
    assert captured["label"] == "2026-06-01 to 2026-06-20"
