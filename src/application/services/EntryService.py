from datetime import datetime
from uuid import uuid4

from src.application.repositories.EntryRepository import EntryRepository
from src.domain.entities.Entry import Entry


class EntryService:

    def __init__(self, repository: EntryRepository):
        self._repository = repository

    def create(
        self,
        title: str,
        content: str,
    ) -> Entry:

        entry = Entry(
            id=str(uuid4()),
            title=title.strip(),
            content=content.strip(),
            last_modified=datetime.now(),
            links=[]
        )

        self._repository.create(entry)

        return entry

    def update(
        self,
        entry_id: str,
        title: str,
        content: str,
    ) -> Entry | None:

        entry = self._repository.get(entry_id)

        if entry is None:
            return None

        entry.title = title.strip()
        entry.content = content.strip()
        entry.last_modified = datetime.now()

        self._repository.update(entry)

        return entry

    def delete(self, entry_id: str) -> None:
        self._repository.delete(entry_id)

    def get(self, entry_id: str) -> Entry | None:
        return self._repository.get(entry_id)

    def get_all(self) -> list[Entry]:
        return self._repository.get_all()