from dataclasses import dataclass, field


@dataclass(slots=True)
class Analysis:
    entry_id: str

    keywords: list[str] = field(default_factory=list)

    relations: dict[str, int] = field(default_factory=dict)

    statistics: dict[str, int] = field(default_factory=dict)