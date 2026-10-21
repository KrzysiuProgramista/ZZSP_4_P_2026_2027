import contextlib
import os
import sqlite3
import tempfile
import shutil

class DatabaseManager:
    def __init__(self, db_name=":memory:"):
        self.db_name = db_name
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_name)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            if exc_type is not None:
                self.conn.rollback()
                print("[DB] Exception occurred. Rolled back.")
            else:
                self.conn.commit()
                print("[DB] Success. Committed.")
            self.conn.close()
        return False


@contextlib.contextmanager
def temp_directory():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        shutil.rmtree(path)

@contextlib.contextmanager
def change_directory(new_path):
    prev_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(prev_path)

@contextlib.contextmanager
def set_env_var(key, value):
    old_value = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old_value is None:
            del os.environ[key]
        else:
            os.environ[key] = old_value


if __name__ == "__main__":
    print("=== EXERCISE 2 TESTS ===")
    
    with DatabaseManager() as db:
        db.execute("CREATE TABLE test (id INT)")
        db.execute("INSERT INTO test VALUES (1)")

    with temp_directory() as tmp:
        print(f"Temp dir created at: {tmp}")

    print(f"Original dir: {os.getcwd()}")
    with change_directory(tempfile.gettempdir()):
        print(f"Inside temp dir: {os.getcwd()}")

    os.environ["MY_VAR"] = "original"
    with set_env_var("MY_VAR", "temporary"):
        print(f"MY_VAR inside: {os.environ.get('MY_VAR')}")
    print(f"MY_VAR after: {os.environ.get('MY_VAR')}")