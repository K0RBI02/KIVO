"""
KIVO Engine
Logging
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


class Logger:

    _configured = False

    @classmethod
    def configure(cls, *, level: int = logging.INFO, log_file: str | Path | None = None) -> None:
        if cls._configured:
            return

        handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

        if log_file is not None:
            handlers.append(logging.FileHandler(log_file))

        logging.basicConfig(
            level=level,
            format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            handlers=handlers,
        )

        cls._configured = True

    @staticmethod
    def get(name: str) -> logging.Logger:
        return logging.getLogger(name)
