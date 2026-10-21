from contextlib import contextmanager
import sqlite3
import shutil
import tempfile
import os

@contextmanager
def managed_database(db_path):
  conn = sqlite3.connect(db_path)
  try:
    yield conn
    conn.commit()  # Commit if no exceptions occurred
  except Exception:
    conn.rollback()  # Rollback if an exception was raised
    raise  # Re-raise the exception
  finally:
    conn.close()  # Always clean up the connection

@contextmanager
def temporary_directory():
  temp_dir = tempfile.mkdtemp()
  try:
    yield temp_dir
  finally:
    shutil.rmtree(temp_dir)  # Clean up the directory and its contents
    
@contextmanager
def working_directory(new_path):
  previous_path = os.getcwd()
  os.chdir(new_path)
  try:
    yield
  finally:
    os.chdir(previous_path)  # Restore original working directory

@contextmanager
def temporary_env(key, value):
  old_value = os.environ.get(key)
  os.environ[key] = str(value)
  try:
    yield
  finally:
    if old_value is None:
      os.environ.pop(key, None)  # Remove if it wasn't there originally
    else:
      os.environ[key] = old_value  # Restore old value

# Create a table and insert data successfully
with managed_database("test.db") as conn:
  cursor = conn.cursor()
  cursor.execute(
      "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
  )
  cursor.execute("INSERT INTO users (name) VALUES ('Alice')")
# Automatically committed and connection closed here!

# Example with an error (triggers rollback)
try:
  with managed_database("test.db") as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES ('Bob')")
    raise RuntimeError(
        "Simulated failure!"
    )  # This triggers a rollback, so 'Bob' won't be saved
except RuntimeError:
  pass

with temporary_directory() as tmp_dir:
  file_path = f"scratch.txt"

  # Write a temporary file
  with open(file_path, "w") as f:
    f.write("Hello, temporary world!")

  print(f"File exists? {os.path.exists(file_path)}")  # Output: True

# Once outside the block, the entire folder and its files are wiped out!

print(f"Original directory: {os.getcwd()}")

# Temporarily move into a subfolder (e.g., 'logs')
with working_directory("./logs"):
  print(f"Inside block: {os.getcwd()}")
  # Perform file operations here...

print(f"Restored directory: {os.getcwd()}")

# Before block
print("API_KEY before:", os.environ.get("API_KEY"))  # Output: None

with temporary_env("API_KEY", "secret_12345"):
  print("API_KEY inside:", os.environ.get("API_KEY"))  # Output: secret_12345

# After block
print(
    "API_KEY after:", os.environ.get("API_KEY")
)  # Output: None (automatically cleaned up)