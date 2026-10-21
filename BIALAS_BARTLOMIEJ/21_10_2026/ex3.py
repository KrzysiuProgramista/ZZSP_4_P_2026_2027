
import os
from contextlib import ExitStack, suppress, closing
from io import StringIO


def main():
    print("1. Two context managers in one with statement")

    with open("exercise3_a.txt", "w") as file_a, open("exercise3_b.txt", "w") as file_b:
        file_a.write("Hello from file A")
        file_b.write("Hello from file B")

    with open("exercise3_a.txt", "r") as file_a, open("exercise3_b.txt", "r") as file_b:
        print(file_a.read())
        print(file_b.read())

    print("\n2. ExitStack with a variable number of files")

    filenames = ["exercise3_a.txt", "exercise3_b.txt"]
    with ExitStack() as stack:
        files = [stack.enter_context(open(name, "r")) for name in filenames]
        for file in files:
            print(f"{file.name}: {file.read()}")

    print("\n3. suppress(FileNotFoundError)")

    with suppress(FileNotFoundError):
        os.remove("file_that_does_not_exist.txt")
    print("Execution continued after suppress")

    try:
        os.remove("another_missing_file.txt")
    except FileNotFoundError:
        pass
    print("Execution continued after try/except/pass")

    print("\n4. closing() with an object that has close() but no __exit__()")

    class CustomResource:
        def __init__(self):
            self.closed = False

        def read(self):
            return "Data from custom resource"

        def close(self):
            self.closed = True
            print("Custom resource closed")

    resource = CustomResource()

    with closing(resource) as item:
        print(item.read())
        print("Resource closed inside with:", item.closed)

    print("Resource closed after with:", resource.closed)

    print("\nAll exercises completed successfully.")


if __name__ == "__main__":
    main()
