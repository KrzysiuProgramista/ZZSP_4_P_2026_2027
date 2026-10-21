import contextlib
import os
import tempfile

@contextlib.contextmanager
def temp_directory():
    path = tempfile.mkdtemp()
    try:
        yield path
    finally:
        import shutil
        shutil.rmtree(path)


if __name__ == "__main__":
    print("=== EXERCISE 3 TESTS ===")

    print("1. Two context managers in one with statement:")
    with temp_directory() as dir1, temp_directory() as dir2:
        print(f"Dir 1: {dir1}")
        print(f"Dir 2: {dir2}")

    print("\n2. ExitStack for multiple files:")
    filenames = []
    for i in range(2):
        f = tempfile.NamedTemporaryFile(delete=False, mode="w")
        f.write(f"content {i}")
        f.close()
        filenames.append(f.name)

    with contextlib.ExitStack() as stack:
        files = [stack.enter_context(open(fname, "r")) for fname in filenames]
        for f in files:
            print(f.read().strip())
    
    for fname in filenames:
        os.remove(fname)

    print("\n3. contextlib.suppress vs try/except/pass:")
    
    with contextlib.suppress(FileNotFoundError):
        os.remove("non_existent_file.txt")
    print("contextlib.suppress handled missing file.")

    try:
        os.remove("non_existent_file.txt")
    except FileNotFoundError:
        pass
    print("try/except/pass handled missing file.")

    print("\n4. contextlib.closing example:")
    class DummyResource:
        def close(self):
            print("DummyResource closed via contextlib.closing!")

    with contextlib.closing(DummyResource()):
        print("Using dummy resource...")