from contextlib import contextmanager
import sqlite3
import shutil
import tempfile
import os


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
    shutil.rmtree(temp_dir, ignore_errors=True)


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


from contextlib import contextmanager
import os


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
  # temporary directory test
  with temporary_directory() as temp_dir:
    print(f"Working inside temp dir: {temp_dir}")

  # environment variable test
  with temporary_env("API_KEY", "secret_123"):
    print(f"API_KEY is set to: {os.environ.get('API_KEY')}")
  print(f"API_KEY after context: {os.environ.get('API_KEY')}")
