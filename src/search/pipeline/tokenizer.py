"""
KIVO Search Engine
Tokenizer

Aufgabe: Text -> Token[]. Sonst nichts.
"""

from __future__ import annotations

import re

_TOKEN_PATTERN = re.compile(r"[a-zA-ZäöüÄÖÜß0-9]+")


class Tokenizer:

    def execute(self, context) -> None:
        context.tokens = self.tokenize(context.raw_query)

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return _TOKEN_PATTERN.findall(text.lower())
