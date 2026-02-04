import sqlite3
from pathlib import Path
from typing import Iterable, Optional


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection: Optional[sqlite3.Connection] = None

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    def initialize(self) -> None:
        cursor = self.connection.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS brand_representatives (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                last_contact TEXT
            );

            CREATE TABLE IF NOT EXISTS meeting_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                meeting_date TEXT NOT NULL,
                notes TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS internal_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                order_date TEXT NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                status TEXT NOT NULL
            );
            """
        )
        self.connection.commit()

    def execute(self, query: str, params: Iterable = ()) -> None:
        cursor = self.connection.cursor()
        cursor.execute(query, tuple(params))
        self.connection.commit()

    def fetch_all(self, query: str, params: Iterable = ()):  # type: ignore[override]
        cursor = self.connection.cursor()
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
