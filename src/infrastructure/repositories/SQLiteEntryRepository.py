from datetime import datetime

from src.application.repositories.EntryRepository import EntryRepository
from src.domain.entities.Entry import Entry
from src.infrastructure.database.Database import Database


class SQLiteEntryRepository(EntryRepository):

    def __init__(self, database: Database):

        self.db = database

    def create(self, entry: Entry) -> None:

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            INSERT INTO entries(
                id,
                title,
                content,
                last_modified
            )
            VALUES(?,?,?,?)
            """,
            (
                entry.id,
                entry.title,
                entry.content,
                entry.last_modified.isoformat()
            )
        )

        self.db.connection.commit()

    def update(self, entry: Entry) -> None:

        cursor = self.db.connection.cursor()

        cursor.execute(
            """
            UPDATE entries
            SET
                title=?,
                content=?,
                last_modified=?
            WHERE id=?
            """,
            (
                entry.title,
                entry.content,
                entry.last_modified.isoformat(),
                entry.id
            )
        )

        self.db.connection.commit()

    def delete(self, entry_id: str) -> None:

        cursor = self.db.connection.cursor()

        cursor.execute(
            "DELETE FROM entries WHERE id=?",
            (entry_id,)
        )

        self.db.connection.commit()

    def get(self, entry_id: str) -> Entry | None:

        cursor = self.db.connection.cursor()

        cursor.execute(
            "SELECT * FROM entries WHERE id=?",
            (entry_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Entry(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            last_modified=datetime.fromisoformat(
                row["last_modified"]
            ),
            links=[]
        )

    def get_all(self) -> list[Entry]:

        cursor = self.db.connection.cursor()

        cursor.execute("""
            SELECT *
            FROM entries
            ORDER BY last_modified DESC
        """)

        rows = cursor.fetchall()

        entries = []

        for row in rows:

            entries.append(
                Entry(
                    id=row["id"],
                    title=row["title"],
                    content=row["content"],
                    last_modified=datetime.fromisoformat(
                        row["last_modified"]
                    ),
                    links=[]
                )
            )

        return entries