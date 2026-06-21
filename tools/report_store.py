from __future__ import annotations

import os
import tempfile
from pathlib import Path


class ReportStore:
    """Writes replaceable reports atomically inside the project storage folder."""

    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def write(self, filename: str, content: str) -> Path:
        if Path(filename).name != filename or not filename.endswith(".md"):
            raise ValueError("Report filename must be a plain Markdown filename.")
        target = self.root / filename
        fd, temporary_name = tempfile.mkstemp(
            dir=self.root, prefix=f".{filename}.", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content.rstrip() + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, target)
        finally:
            temporary = Path(temporary_name)
            if temporary.exists():
                temporary.unlink()
        return target
