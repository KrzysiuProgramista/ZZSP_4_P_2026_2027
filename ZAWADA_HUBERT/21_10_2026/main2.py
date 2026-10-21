import contextlib
import os

print("--- 1. Two Context Managers in One with Statement ---")
with open("file1.txt", "w") as f1, open("file2.txt", "w") as f2:
  f1.write("Data for file 1")
  f2.write("Data for file 2")
print("Files created and written successfully.")


print("\n--- 2. Using contextlib.ExitStack for Variable Files ---")


def read_all_files(filenames):
  with contextlib.ExitStack() as stack:
    files = [stack.enter_context(open(fname, "r")) for fname in filenames]
    contents = [f.read() for f in files]
    return contents


file_contents = read_all_files(["file1.txt", "file2.txt"])
print(f"Contents read via ExitStack: {file_contents}")


print("\n--- 3. contextlib.suppress vs try/except/pass ---")

with contextlib.suppress(FileNotFoundError):
  os.remove("non_existent_file.txt")
  print("File removed successfully.")
print("Handled FileNotFoundError cleanly with suppress.")

try:
  os.remove("non_existent_file.txt")
  print("File removed successfully.")
except FileNotFoundError:
  pass
print("Handled FileNotFoundError with try/except/pass.")


print("\n--- 4. Using contextlib.closing on Legacy Objects ---")


class LegacyDatabaseConnection:

  def close(self):
    print("Legacy connection closed safely!")


with contextlib.closing(LegacyDatabaseConnection()) as db:
  print("Performing queries on legacy database...")


for fname in ["file1.txt", "file2.txt"]:
  with contextlib.suppress(FileNotFoundError):
    os.remove(fname)