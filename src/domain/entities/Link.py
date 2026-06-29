from dataclasses import dataclass

from src.domain.enums.LinkType import LinkType


@dataclass(slots=True)
class Link:
    target_id: str
    title: str
    type: LinkType