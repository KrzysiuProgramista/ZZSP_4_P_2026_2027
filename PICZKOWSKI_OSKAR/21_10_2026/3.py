import os
from contextlib import contextmanager, ExitStack, suppress, closing
from pathlib import Path

@contextmanager
def resource(name):
    print(f"{name}: acquired")
    try:
        yield
    finally:
        print(f"{name}: released")


with resource("A"), resource("B"):
    print("Using both resources")



filenames = ["file1.txt", "file2.txt", "file3.txt"]

for filename in filenames:
    Path(filename).write_text(f"Contents of {filename}")

with ExitStack() as stack:
    files = [
        stack.enter_context(open(filename, "r", encoding="utf-8"))
        for filename in filenames
    ]

    for file in files:
        print(file.read())



with suppress(FileNotFoundError):
    os.remove("does_not_exist.txt")

print("Missing file ignored using suppress()")

try:
    os.remove("does_not_exist.txt")
except FileNotFoundError:
    pass

print("Missing file ignored using try/except/pass")


class ResourceWithoutContextManager:
    def use(self):
        print("Using resource")

    def close(self):
        print("Resource closed")


resource_object = ResourceWithoutContextManager()

with closing(resource_object) as resource_instance:
    resource_instance.use()


class ExceptionSuppressor:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is ZeroDivisionError:
            print("ZeroDivisionError suppressed")
            return True
        return False


with ExceptionSuppressor():
    1 / 0

print("Program continues after suppressed exception")
