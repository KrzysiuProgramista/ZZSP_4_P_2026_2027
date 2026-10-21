import os
import sqlite3
import tempfile
import shutil
from contextlib import contextmanager


@contextmanager
def database_connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def temporary_directory():
    directory = tempfile.mkdtemp()
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


@contextmanager
def change_directory(path):
    original_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_directory)


@contextmanager
def temporary_environment_variable(name, value):
    existed = name in os.environ
    old_value = os.environ.get(name)
    try:
        os.environ[name] = value
        yield
    finally:
        if existed:
            os.environ[name] = old_value
        else:
            os.environ.pop(name, None)


if __name__ == "__main__":
    with database_connection("example.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
        """)
        cursor.execute(
            "INSERT INTO users (name) VALUES (?)",
            ("Alice",)
        )

    with temporary_directory() as path:
        print("Temporary directory:", path)
        file_path = os.path.join(path, "example.txt")
        with open(file_path, "w") as file:
            file.write("Hello, world!")

    with change_directory(tempfile.gettempdir()):
        print("Current directory:", os.getcwd())

    with temporary_environment_variable("MY_TEMP_VARIABLE", "hello"):
        print(os.environ["MY_TEMP_VARIABLE"])

    print(os.environ.get("MY_TEMP_VARIABLE"))
