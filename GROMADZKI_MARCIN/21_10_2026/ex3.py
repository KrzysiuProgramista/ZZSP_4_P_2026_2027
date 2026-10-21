import contextlib
import os
import tempfile

def run_exercises():
    with tempfile.TemporaryDirectory() as tmp_dir, change_directory(tmp_dir):
        print(f"Current working directory inside context: {os.getcwd()}")

    file_names = ['file1.txt', 'file2.txt']
    for fname in file_names:
        with open(fname, 'w') as f:
            f.write("Hello world")

    try:
        with contextlib.ExitStack() as stack:
            files = [stack.enter_context(open(fname, 'r')) for fname in file_names]
            contents = [f.read() for f in files]
            print("Successfully read files using ExitStack:", contents)
    finally:
        for fname in file_names:
            if os.path.exists(fname):
                os.remove(fname)


    with contextlib.suppress(FileNotFoundError):
        os.remove("non_existent_file.txt")

    try:
        os.remove("non_existent_file.txt")
    except FileNotFoundError:
        pass

    class CustomResource:
        def close(self):
            print("CustomResource closed via contextlib.closing!")

    with contextlib.closing(CustomResource()) as resource:
        print("Inside closing context block")

@contextlib.contextmanager
def change_directory(path):
    prev_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_dir)

if __name__ == "__main__":
    run_exercises()