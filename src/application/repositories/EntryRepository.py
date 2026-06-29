from abc import ABC, abstractmethod

from src.domain.entities.Entry import Entry


class EntryRepository(ABC):

    @abstractmethod
    def create(self, entry: Entry) -> None:
        ...

    @abstractmethod
    def update(self, entry: Entry) -> None:
        ...

    @abstractmethod
    def delete(self, entry_id: str) -> None:
        ...

    @abstractmethod
    def get(self, entry_id: str) -> Entry | None:
        ...

    @abstractmethod
    def get_all(self) -> list[Entry]:
        ...