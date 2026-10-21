import contextlib

with open("test1.txt", "w") as f1, open("test2.txt", "w") as f2:
    f1.write("file one")
    f2.write("file two")
print("Multiple files written")

filenames = ["test1.txt", "test2.txt"]
with contextlib.ExitStack() as stack:
    opened = [stack.enter_context(open(name)) for name in filenames]
    for f in opened:
        print(f.read())

with contextlib.suppress(FileNotFoundError):
    open("fake.txt")
print("Handled with contextlib.suppress")

try:
    open("fake.txt")
except FileNotFoundError:
    pass
print("Handled with try-except")

class CustomObject:
    def close(self):
        print("Custom object closed")

with contextlib.closing(CustomObject()):
    print("Using custom object")