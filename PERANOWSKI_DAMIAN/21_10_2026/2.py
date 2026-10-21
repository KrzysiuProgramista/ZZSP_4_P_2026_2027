import os
import tempfile
from contextlib import contextmanager

@contextmanager
def mock_db():
    print("Database connected")
    try:
        yield "db_connection"
        print("Database committed")
    except:
        print("Database rolled back")
        raise

@contextmanager
def temp_dir():
    d = tempfile.mkdtemp()
    print("Created temp dir:", d)
    try:
        yield d
    finally:
        os.rmdir(d)
        print("Removed temp dir:", d)

@contextmanager
def change_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)

@contextmanager
def temp_env(key, value):
    old = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old is None:
            del os.environ[key]
        else:
            os.environ[key] = old

with mock_db() as db:
    print("Working with", db)

with temp_dir() as d:
    print("Inside temp dir")

with change_dir(tempfile.gettempdir()):
    print("Changed dir to:", os.getcwd())

with temp_env("MY_VAR", "hello"):
    print("Env var:", os.environ.get("MY_VAR"))