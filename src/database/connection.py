"""
src/database/connection.py

Sprint 1 - Day 04
SQLite Database Connection
"""

from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = PROJECT_ROOT / "db" / "nifty100.db"

SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(DATABASE_PATH)

        self.connection.execute("PRAGMA foreign_keys = ON")

        self.cursor = self.connection.cursor()

    def create_schema(self):

        with open(SCHEMA_PATH, "r", encoding="utf-8") as file:

            schema = file.read()

        self.cursor.executescript(schema)

        self.connection.commit()

        print("Database schema created successfully.")

    def show_tables(self):

        self.cursor.execute("""

            SELECT name

            FROM sqlite_master

            WHERE type='table'

            ORDER BY name;

        """)

        tables = self.cursor.fetchall()

        print("\nAvailable Tables\n")

        for table in tables:

            print(f"• {table[0]}")

    def close(self):

        self.connection.close()


if __name__ == "__main__":

    db = Database()

    db.create_schema()

    db.show_tables()

    db.close()