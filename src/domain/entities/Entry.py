from dataclasses import dataclass, field
from datetime import datetime

from src.domain.entities.Link import Link


@dataclass(slots=True)
class Entry:
    id: str
    title: str
    content: str
    last_modified: datetime
    links: list[Link] = field(default_factory=list)