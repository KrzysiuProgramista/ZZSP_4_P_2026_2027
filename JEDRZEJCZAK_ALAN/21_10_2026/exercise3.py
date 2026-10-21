
import os
import tempfile
from contextlib import ExitStack, suppress, closing


# 1. Two context managers in one with statement
with tempfile.TemporaryDirectory() as folder:
    file1 = os.path.join(folder, "file1.txt")
    file2 = os.path.join(folder, "file2.txt")

    with open(file1, "w") as f1, open(file2, "w") as f2:
        f1.write("Hello from file 1")
        f2.write("Hello from file 2")

    print("Both files created")


    # 2. ExitStack - variable number of files
    filenames = [file1, file2]

    with ExitStack() as stack:
        files = [
            stack.enter_context(open(name, "r"))
            for name in filenames
        ]

        for file in files:
            print(file.read())

    print("All files closed")


    # 3. suppress vs try/except/pass
    missing = os.path.join(folder, "missing.txt")

    # Using suppress
    with suppress(FileNotFoundError):
        open(missing, "r")

    print("Suppress: program continues")

    # Using try/except
    try:
        open(missing, "r")
    except FileNotFoundError:
        pass

    print("Try/except: program continues")


# 4. closing - object without __exit__
class Resource:
    def __init__(self):
        self.closed = False

    def do_something(self):
        print("Resource is working")

    def close(self):
        self.closed = True
        print("Resource closed")


with closing(Resource()) as resource:
    resource.do_something()

print("Closed:", resource.closed)
