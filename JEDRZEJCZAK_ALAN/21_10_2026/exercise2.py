
import os
import sqlite3
import tempfile
import shutil
from contextlib import contextmanager


# 1. Database connection
@contextmanager
def database_connection(db_name):
    conn = sqlite3.connect(db_name)
    try:
        yield conn
    except Exception:
        conn.rollback()
        print("Transaction rolled back")
        raise
    else:
        conn.commit()
        print("Transaction committed")
    finally:
        conn.close()
        print("Connection closed")


# 2. Temporary directory
@contextmanager
def temporary_directory():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)
        print("Temporary directory removed")


# 3. Change working directory
@contextmanager
def change_directory(path):
    old_directory = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old_directory)
        print("Original directory restored")


# 4. Temporary environment variable
@contextmanager
def temporary_env(key, value):
    old_value = os.environ.get(key)
    os.environ[key] = value

    try:
        yield
    finally:
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value

        print("Environment variable restored")


# TESTS

# Test 1 - Database
with database_connection(":memory:") as db:
    db.execute("CREATE TABLE users (id INTEGER)")
    db.execute("INSERT INTO users VALUES (1)")

# Test 2 - Temporary directory
with temporary_directory() as folder:
    print("Temporary directory:", folder)

# Test 3 - Working directory
with temporary_directory() as folder:
    with change_directory(folder):
        print("Current directory:", os.getcwd())

# Test 4 - Environment variable
with temporary_env("MODE", "DEBUG"):
    print("Inside:", os.environ["MODE"])

print("Outside:", os.environ.get("MODE"))
