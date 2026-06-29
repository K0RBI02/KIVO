from dataclasses import dataclass


@dataclass(slots=True)
class SearchResult:
    id: str
    title: str
    preview: str
    score: float