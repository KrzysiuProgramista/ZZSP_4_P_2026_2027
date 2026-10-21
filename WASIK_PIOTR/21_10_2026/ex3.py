
from contextlib import ExitStack, suppress, closing
import tempfile
from pathlib import Path
import os


# ============================================================
# EXERCISE 3: Nested and multiple
# ============================================================


# 1. Use two context managers in one with statement

print("Exercise 3.1 - Two context managers")

with tempfile.TemporaryDirectory() as directory, open(
    os.path.join(directory, "example.txt"), "w"
) as file:
    file.write("Hello from two context managers!")
    print("File created inside:", directory)

print("Both context managers have finished.")


# 2. Use ExitStack to open a variable number of files

print("\nExercise 3.2 - ExitStack")

with tempfile.TemporaryDirectory() as directory:
    filenames = ["file1.txt", "file2.txt", "file3.txt"]

    # Create example files
    for filename in filenames:
        path = Path(directory) / filename
        path.write_text(f"Contents of {filename}")

    # Open a variable number of files
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(Path(directory) / filename, "r"))
            for filename in filenames
        ]

        for file in files:
            print(file.read())

    # ExitStack closes all opened files automatically
    print("All files have been closed.")


# 3. Use suppress(FileNotFoundError) and compare
#    with try/except/pass

print("\nExercise 3.3 - suppress vs try/except/pass")

missing_file = "file_that_does_not_exist.txt"

# Method 1: try/except/pass
try:
    os.remove(missing_file)
except FileNotFoundError:
    pass

print("try/except/pass: missing file ignored.")

# Method 2: contextlib.suppress
with suppress(FileNotFoundError):
    os.remove(missing_file)

print("suppress: missing file ignored.")

# Both approaches ignore the same exception.
# suppress is shorter and more readable for this simple case.


# 4. Use closing on an object that has close()
#    but does not implement __enter__() or __exit__()

print("\nExercise 3.4 - closing")


class MyResource:
    def __init__(self):
        self.closed = False

    def use(self):
        print("Resource is being used.")

    def close(self):
        self.closed = True
        print("Resource has been closed.")


resource = MyResource()

# MyResource has close(), but no __enter__() or __exit__().
# closing() ensures close() is called when the with block ends.
with closing(resource) as item:
    item.use()
    print("Closed inside with:", item.closed)

print("Closed after with:", resource.closed)
