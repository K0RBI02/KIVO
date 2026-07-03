"""
KIVO Search Engine
Pipeline

Genau das Prinzip aus der Spec:
    for module in modules:
        data = module.execute(data)

Jedes Modul kennt nur seine eigene Aufgabe. Module ergaenzen statt
bestehende umzubauen.
"""

from __future__ import annotations

from .context import PipelineContext


class Pipeline:

    def __init__(self, modules: list) -> None:
        self._modules = modules

    def run(self, raw_query: str) -> PipelineContext:
        context = PipelineContext(raw_query=raw_query)

        for module in self._modules:
            module.execute(context)

        return context
