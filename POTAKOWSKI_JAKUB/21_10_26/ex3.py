from contextlib import ExitStack, suppress, closing
import os


class MyResource:
    def use(self):
        print("Using resource.")

    def close(self):
        print("Resource closed.")


if __name__ == "__main__":
    with open("input.txt", "w") as file:
        file.write("Hello, Python!")

    with open("input.txt", "r") as source, \
         open("output.txt", "w") as destination:
        content = source.read()
        destination.write(content.upper())

    with open("output.txt", "r") as file:
        print(file.read())

    filenames = ["input.txt", "output.txt"]

    with ExitStack() as stack:
        files = [
            stack.enter_context(open(name, "r"))
            for name in filenames
        ]

        for file in files:
            print(file.read())

    with suppress(FileNotFoundError):
        os.remove("missing.txt")

    try:
        os.remove("missing.txt")
    except FileNotFoundError:
        pass

    with closing(MyResource()) as resource:
        resource.use()
