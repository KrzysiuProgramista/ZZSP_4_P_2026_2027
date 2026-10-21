import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path


class DBConn:
    def __init__(self, database: str | Path):
        self.database = database
        self.conn: sqlite3.Connection | None = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.database)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS kv (
                name TEXT PRIMARY KEY,
                value INTEGER NOT NULL
            )
        """)
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
        finally:
            self.conn.close()
            self.conn = None

        return False  # Don't suppress exceptions

    def read(self, name: str) -> int | None:
        row = self.conn.execute(
            "SELECT value FROM kv WHERE name = ?", (name,)
        ).fetchone()
        return row[0] if row is not None else None

    def write(self, name: str, val: int) -> None:
        self.conn.execute(
            """
            INSERT INTO kv (name, value) VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET value = excluded.value
            """,
            (name, val),
        )


@contextmanager
def temporary_directory():
    path = tempfile.mkdtemp()
    try:
        yield Path(path)
    finally:
        # Removes the directory and everything inside it.
        import shutil
        shutil.rmtree(path)


@contextmanager
def working_directory(path):
    old_directory = os.getcwd()
    os.chdir(path)
    try:
        yield Path.cwd()
    finally:
        os.chdir(old_directory)


@contextmanager
def temporary_environment_variable(name: str, value: str):
    existed = name in os.environ
    old_value = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if existed:
            os.environ[name] = old_value
        else:
            os.environ.pop(name, None)



with DBConn("data.sqlite") as db:
    db.write("answer", 42)

with DBConn("data.sqlite") as db:
    print(db.read("answer"))  # 42

with temporary_directory() as temp_path:
    (temp_path / "note.txt").write_text("temporary")

with working_directory("/tmp"):
    print(Path.cwd())

with temporary_environment_variable("APP_MODE", "test"):
    print(os.environ["APP_MODE"])

