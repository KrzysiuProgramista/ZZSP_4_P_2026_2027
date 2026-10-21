"""Exercise 2: Resource management. Run: python exercise2.py"""

import os
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path


# 1. Commit on success, roll back on error, always close.
@contextmanager
def database_connection(path):
    connection = sqlite3.connect(path)
    try:
        yield connection
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


# 2. Remove the directory even if the block raises an exception.
@contextmanager
def temporary_directory():
    directory = Path(tempfile.mkdtemp())
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


# 3. Restore the original working directory.
@contextmanager
def working_directory(path):
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield Path.cwd()
    finally:
        os.chdir(previous)


# 4. Restore the previous value, or remove a newly created variable.
@contextmanager
def environment_variable(name, value):
    previous = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = previous


# Working directory and environment changes affect the whole process.
def main():
    original_directory = Path.cwd()
    original_value = os.environ.get("EXERCISE_MODE")

    with temporary_directory() as directory:
        database = directory / "example.db"
        with database_connection(database) as connection:
            connection.execute("CREATE TABLE users (name TEXT)")
            connection.execute("INSERT INTO users VALUES (?)", ("Hubert",))

        try:
            with database_connection(database) as connection:
                connection.execute("INSERT INTO users VALUES (?)", ("Rolled back",))
                raise ValueError("Example transaction failure")
        except ValueError:
            print("Failed transaction rolled back.")

        with database_connection(database) as connection:
            rows = connection.execute("SELECT name FROM users").fetchall()
            assert rows == [("Hubert",)]
            print("Saved rows:", rows)

        with working_directory(directory):
            print("Temporary working directory:", Path.cwd())
        assert Path.cwd() == original_directory

        with environment_variable("EXERCISE_MODE", "testing"):
            assert os.environ["EXERCISE_MODE"] == "testing"
            print("Temporary environment value:", os.environ["EXERCISE_MODE"])
        assert os.environ.get("EXERCISE_MODE") == original_value

    assert not directory.exists()
    print("Directory removed; working directory and environment restored.")


if __name__ == "__main__":
    main()
