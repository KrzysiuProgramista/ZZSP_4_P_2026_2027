
import os
import sqlite3
import tempfile
from contextlib import contextmanager


@contextmanager
def database_connection(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    except BaseException:
        conn.rollback()
        raise
    else:
        conn.commit()
    finally:
        conn.close()


@contextmanager
def temporary_directory():
    with tempfile.TemporaryDirectory() as path:
        yield path


@contextmanager
def working_directory(path):
    original_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original_dir)


@contextmanager
def temporary_environment_variable(name, value):
    existed = name in os.environ
    original_value = os.environ.get(name)
    os.environ[name] = str(value)
    try:
        yield
    finally:
        if existed:
            os.environ[name] = original_value
        else:
            os.environ.pop(name, None)


def main():
    print("Testing database connection...")
    with database_connection("exercise.db") as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)"
        )
        conn.execute("INSERT INTO test (name) VALUES (?)", ("Alice",))
        print("Database insert successful")
    print("Database committed and connection closed\n")

    print("Testing temporary directory...")
    with temporary_directory() as path:
        print("Temporary directory created:", os.path.exists(path))
        with open(os.path.join(path, "test.txt"), "w") as f:
            f.write("Hello")
        print("File created:", os.path.exists(os.path.join(path, "test.txt")))
    print("Temporary directory removed:", not os.path.exists(path), "\n")

    print("Testing working directory...")
    original = os.getcwd()
    with tempfile.TemporaryDirectory() as path:
        with working_directory(path):
            print("Changed directory:", os.getcwd() == path)
        print("Original directory restored:", os.getcwd() == original)
    print()

    print("Testing environment variable...")
    variable = "EXERCISE_TEST_VARIABLE"
    os.environ.pop(variable, None)
    with temporary_environment_variable(variable, "hello"):
        print("Variable set:", os.environ.get(variable) == "hello")
    print("Variable restored:", variable not in os.environ)

    print("\nAll tests completed successfully.")


if __name__ == "__main__":
    main()
