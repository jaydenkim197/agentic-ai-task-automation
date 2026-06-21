from pathlib import Path

from tools.report_store import ReportStore


def test_report_store_replaces_report_atomically(tmp_path: Path):
    store = ReportStore(tmp_path / "storage")
    target = store.write("important_emails.md", "first")
    assert target.read_text(encoding="utf-8") == "first\n"
    store.write("important_emails.md", "second")
    assert target.read_text(encoding="utf-8") == "second\n"
