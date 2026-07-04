"""
KIVO Engine
Execution Context

Verhindert Endlosschleifen in Rule-Ketten
(Rule A erzeugt Node -> triggert Rule B -> erzeugt Node -> ...).
"""

from __future__ import annotations


class ExecutionContext:

    def __init__(self, max_depth: int = 10) -> None:
        self.depth = 0
        self.max_depth = max_depth

    def enter(self) -> None:
        self.depth += 1
        if self.depth > self.max_depth:
            raise RuntimeError(
                f"Rule recursion limit reached (max_depth={self.max_depth})."
            )

    def exit(self) -> None:
        self.depth = max(0, self.depth - 1)
