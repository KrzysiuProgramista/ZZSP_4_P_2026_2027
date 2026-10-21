from contextlib import ExitStack, closing, suppress
from pathlib import Path
from io import BytesIO



with open("input.txt", encoding="utf-8") as source, \
    open("output.txt", "w", encoding="utf-8") as destination:
    destination.write(source.read())



filenames = ["a.txt", "b.txt", "c.txt"]

with ExitStack() as stack:
    files = [
        stack.enter_context(open(name, encoding="utf-8"))
        for name in filenames
    ]
    contents = [file.read() for file in files]
    for content in contents:
        print(f"Content: {content}")



with suppress(FileNotFoundError):
    Path("optional.txt").unlink()
    print("Suppress: File found")

try:
    Path("optional.txt").unlink()
    print("Try: File found")
except FileNotFoundError:
    print("Try: File not found")



buffer = BytesIO(b"Hello")

with closing(buffer) as stream:
    print(stream.read())
