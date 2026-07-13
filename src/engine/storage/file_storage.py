"""
KIVO Engine
File Storage
"""

import os
import tempfile
import contextlib

from pathlib import Path
from typing import Any

from .serializer import Serializer


class FileStorage:
    """Einfacher dateibasierter Speicher."""

    def __init__(self, path: str | Path, serializer: Serializer) -> None:
        self.path = Path(path)
        self.serializer = serializer
        self.path.mkdir(parents=True, exist_ok=True)

    def save(self, name: str, data: Any) -> Path:
        file_path = self.path / f"{name}.json"
        serialized = self.serializer.serialize(data)

        fd, tmp_name = tempfile.mkstemp(dir=self.path, prefix=f".{name}.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                tmp_file.write(serialized)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            os.replace(tmp_name, file_path)  # atomar auf Windows & Unix
        except Exception:
            with contextlib.suppress(FileNotFoundError):
                os.remove(tmp_name)
            raise

        return file_path

    def load(self, name: str) -> Any:
        file_path = self.path / f"{name}.json"
        if not file_path.exists():
            return None
        content = file_path.read_text(encoding="utf-8")
        return self.serializer.deserialize(content)

    def delete(self, name: str) -> None:
        file_path = self.path / f"{name}.json"
        if file_path.exists():
            file_path.unlink()

    def exists(self, name: str) -> bool:
        return (self.path / f"{name}.json").exists()

    def list_files(self) -> list[str]:
        return [file.stem for file in self.path.glob("*.json")]
