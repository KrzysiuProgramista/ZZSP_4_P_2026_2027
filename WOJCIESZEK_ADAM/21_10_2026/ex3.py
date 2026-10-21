import os
from contextlib import suppress, closing, ExitStack


with open("file1.txt", "w") as f1, open("file2.txt", "w") as f2:
  f1.write("Data for file 1")
  f2.write("Data for file 2")

file_paths = ["log1.txt", "log2.txt", "log3.txt"]

with ExitStack() as stack:
  # Dynamically open all files and register them with the stack
  opened_files = [stack.enter_context(open(path, "w")) for path in file_paths]

  for f, path in zip(opened_files, file_paths):
    f.write(f"Writing to {path}\n")

# All files in the list are automatically closed here, regardless of errors

file_to_delete = "temporary_scratch.txt"

with suppress(FileNotFoundError):
  os.remove(file_to_delete)

class LegacyDatabaseConnection:
  """A mock legacy class with a .close() method but no context manager support."""

  def connect(self):
    print("Legacy connection established.")

  def close(self):
    print("Legacy connection explicitly closed.")


# Using closing() ensures .close() is called automatically upon exiting the block
with closing(LegacyDatabaseConnection()) as db:
  db.connect()
  print("Doing work with database...")