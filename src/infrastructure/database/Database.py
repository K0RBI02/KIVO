import sqlite3
from pathlib import Path


class Database:

    def __init__(self, database: str = "knowledge.db"):

        self.path = Path(database)

        self.connection = sqlite3.connect(self.path)

        self.connection.row_factory = sqlite3.Row

        self._create_tables()

    def _create_tables(self):

        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries(
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                last_modified TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                title TEXT NOT NULL,
                type TEXT NOT NULL
            )
        """)

        self.connection.commit()