from pathlib import Path

import pytest

from security.guards import (
    SecurityError,
    atomic_write_new,
    ensure_allowed_user,
    ensure_within_root,
    safe_output_path,
)
from tools.ocr_tool import OCRInputError, OCRTool


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


def test_unreadable_pdf_fails_without_creating_output(tmp_path: Path):
    root = tmp_path / "root"
    root.mkdir()
    pdf = root / "placeholder.pdf"
    pdf.write_bytes(b"not a real PDF")
    tool = OCRTool(None, "unused", root, 20, 160, 5, 2)
    with pytest.raises(OCRInputError):
        tool.process(pdf)
    assert not (root / "placeholder_ag.txt").exists()
