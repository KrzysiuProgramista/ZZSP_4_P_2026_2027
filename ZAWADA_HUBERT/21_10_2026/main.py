import os
import shutil
import sqlite3
import tempfile
from contextlib import contextmanager


@contextmanager
def db_transaction(db_path):
  conn = sqlite3.connect(db_path)
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
  temp_dir = tempfile.mkdtemp()
  try:
    yield temp_dir
  finally:
    shutil.rmtree(temp_dir)


@contextmanager
def change_directory(new_path):
  original_path = os.getcwd()
  os.chdir(new_path)
  try:
    yield
  finally:
    os.chdir(original_path)


@contextmanager
def temporary_env(key, value):
  original_value = os.environ.get(key)
  os.environ[key] = value
  try:
    yield
  finally:
    if original_value is None:
      del os.environ[key]
    else:
      os.environ[key] = original_value


if __name__ == "__main__":
  with temporary_directory() as tmp_dir:
    db_file = os.path.join(tmp_dir, "test.db")

    with db_transaction(db_file) as conn:
      cursor = conn.cursor()
      cursor.execute("CREATE TABLE items (name TEXT)")
      cursor.execute("INSERT INTO items VALUES ('apple')")
      print("Database transaction successful!")

  # 2. Temporary environment variable
  with temporary_env("MY_VAR", "hello_world"):
    print(f"MY_VAR inside context: {os.environ.get('MY_VAR')}")

  print(f"MY_VAR outside context: {os.environ.get('MY_VAR')}")