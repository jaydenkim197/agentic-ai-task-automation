from pathlib import Path

import pytest

from security.guards import (
    SecurityError,
    atomic_write_new,
    ensure_allowed_user,
    ensure_within_root,
    safe_output_path,
)
from tools.ocr_tool import OCRIndexAccessError, OCRInputError, OCRTool


def test_only_owner_is_allowed():
    ensure_allowed_user(123, 123)
    with pytest.raises(SecurityError):
        ensure_allowed_user(456, 123)


def test_path_escape_is_blocked(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    with pytest.raises(SecurityError):
        ensure_within_root(tmp_path / "outside.pdf", root)


def test_ocr_name_and_no_overwrite(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    pdf = root / "lecture.pdf"
    pdf.touch()
    output = safe_output_path(pdf, root)
    assert output.name == "lecture_ag.txt"
    atomic_write_new(output, "first", root)
    with pytest.raises(FileExistsError):
        safe_output_path(pdf, root)
    with pytest.raises(FileExistsError):
        atomic_write_new(output, "second", root)
    assert output.read_text() == "first"


def test_pdf_index_respects_depth_and_extension(tmp_path: Path):
    root = tmp_path / "root"
    (root / "course").mkdir(parents=True)
    (root / "course" / "lecture.pdf").touch()
    (root / "course" / "notes.txt").touch()
    tool = OCRTool(None, "unused", root, 20, 160, 5, 2)
    candidates = tool.find_candidates("lecture")
    assert [item.path.name for item in candidates] == ["lecture.pdf"]


def test_pdf_search_refreshes_stale_index_after_no_match(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    tool = OCRTool(None, "unused", root, 20, 160, 5, 2)

    assert tool.find_candidates("robotics") == []
    (root / "robotics_week10.pdf").touch()

    candidates = tool.find_candidates("robotics week10")
    assert [item.path.name for item in candidates] == ["robotics_week10.pdf"]


def test_pdf_search_refreshes_even_when_stale_index_has_similar_matches(
    tmp_path: Path,
):
    root = tmp_path / "root"
    root.mkdir()
    (root / "robotics_week1.pdf").touch()
    tool = OCRTool(None, "unused", root, 20, 160, 5, 2)
    tool.refresh_index()

    (root / "robotics_week11.pdf").touch()
    candidates = tool.find_candidates("robotics week11")

    assert candidates[0].path.name == "robotics_week11.pdf"


def test_nonempty_inaccessible_style_root_is_not_reported_as_no_match(
    tmp_path: Path, monkeypatch
):
    root = tmp_path / "root"
    root.mkdir()
    (root / "visible-folder").mkdir()
    tool = OCRTool(None, "unused", root, 20, 160, 5, 2)

    monkeypatch.setattr("tools.ocr_tool.os.walk", lambda *args, **kwargs: [])

    with pytest.raises(OCRIndexAccessError):
        tool.find_candidates("lecture")


def test_unreadable_pdf_fails_without_creating_output(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    pdf = root / "placeholder.pdf"
    pdf.write_bytes(b"not a real PDF")
    tool = OCRTool(None, "unused", root, 20, 160, 5, 2)
    with pytest.raises(OCRInputError):
        tool.process(pdf)
    assert not (root / "placeholder_ag.txt").exists()


def test_pdf_larger_than_batch_limit_is_processed_completely(
    tmp_path: Path, monkeypatch
):
    import fitz

    root = tmp_path / "root"
    root.mkdir()
    pdf = root / "long-lecture.pdf"
    document = fitz.open()
    for _ in range(21):
        document.new_page()
    document.save(pdf)
    document.close()

    tool = OCRTool(None, "unused", root, 20, 72, 5, 2)
    monkeypatch.setattr(tool, "_render_page", lambda page: b"image")
    monkeypatch.setattr(tool, "_transcribe_page", lambda image: "page text")

    result = tool.process(pdf)

    assert result.pages_processed == 21
    assert result.output.name == "long-lecture_ag.txt"
    assert result.output.read_text().count("--- Page ") == 21
