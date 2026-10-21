
import os
import sqlite3
import tempfile
from contextlib import contextmanager
from pathlib import Path


# ==================================================
# EXERCISE 2: Resource management
# ==================================================


# 1. Database connection context manager
# Commits on success, rolls back on exception,
# and always closes the connection.

@contextmanager
def database_connection(database):
    connection = sqlite3.connect(database)

    try:
        yield connection
    except Exception:
        connection.rollback()
        raise
    else:
        connection.commit()
    finally:
        connection.close()


print("1. DATABASE CONNECTION")

with database_connection(":memory:") as connection:
    connection.execute(
        "CREATE TABLE users (id INTEGER, name TEXT)"
    )
    connection.execute(
        "INSERT INTO users VALUES (?, ?)",
        (1, "Alice")
    )
    print("User inserted successfully.")

print("Database connection closed.")


# 2. Temporary directory context manager
# Creates a directory and removes it afterwards.

@contextmanager
def temporary_directory():
    with tempfile.TemporaryDirectory() as directory:
        yield directory


print("\n2. TEMPORARY DIRECTORY")

with temporary_directory() as directory:
    print("Directory created:", os.path.exists(directory))

    file_path = Path(directory) / "example.txt"
    file_path.write_text("Hello!", encoding="utf-8")

    print("File contents:", file_path.read_text(encoding="utf-8"))

print("Directory removed:", not os.path.exists(directory))


# 3. Working directory context manager
# Changes the current directory and restores it afterwards.

@contextmanager
def change_directory(path):
    original_directory = os.getcwd()

    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original_directory)


print("\n3. WORKING DIRECTORY")

original_directory = os.getcwd()

with tempfile.TemporaryDirectory() as directory:
    with change_directory(directory):
        print("Current directory:", os.getcwd())

    print("Directory restored:", os.getcwd() == original_directory)


# 4. Environment variable context manager
# Temporarily sets a variable and restores its previous state.

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


print("\n4. ENVIRONMENT VARIABLE")

variable_name = "EXERCISE_TEST_VARIABLE"
old_existed = variable_name in os.environ
old_value = os.environ.get(variable_name)

try:
    with temporary_environment_variable(variable_name, "hello"):
        print("Inside with:", os.environ[variable_name])

    print("Variable restored:", variable_name not in os.environ)
finally:
    # Restore the original state after the test as well.
    if old_existed:
        os.environ[variable_name] = old_value
    else:
        os.environ.pop(variable_name, None)


print("\nAll four exercises completed successfully.")
