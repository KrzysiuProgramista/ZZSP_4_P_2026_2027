import os
import sqlite3
import tempfile
import shutil
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def database_connection(connect):
    connection = connect()
    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


with database_connection(lambda: sqlite3.connect(":memory:")) as conn:
    conn.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
    )
    conn.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    print("Database: transaction committed")



try:
    with database_connection(lambda: sqlite3.connect(":memory:")) as conn:
        conn.execute("CREATE TABLE test (id INTEGER)")
        raise ValueError("Simulated database error")
except ValueError:
    print("Database: transaction rolled back")



@contextmanager
def temporary_directory():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)


with temporary_directory() as directory:
    file_path = Path(directory) / "example.txt"
    file_path.write_text("Hello, world!")
    print("Temporary directory:", directory)
    print("File contents:", file_path.read_text())

print("Temporary directory removed")



@contextmanager
def change_directory(path):
    old_directory = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old_directory)


original_directory = os.getcwd()

with change_directory(tempfile.gettempdir()):
    print("Working directory inside:", os.getcwd())

print("Working directory restored:", os.getcwd() == original_directory)



@contextmanager
def temporary_env(name, value):
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


with temporary_env("MY_VARIABLE", "hello"):
    print("Environment variable inside:", os.environ["MY_VARIABLE"])

print("Environment variable restored:", "MY_VARIABLE" not in os.environ)
