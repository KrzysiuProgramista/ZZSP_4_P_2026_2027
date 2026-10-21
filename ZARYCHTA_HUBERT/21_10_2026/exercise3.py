"""Exercise 3: Nested and multiple. Run: python exercise3.py"""

from contextlib import ExitStack, closing, suppress
from pathlib import Path
from tempfile import TemporaryDirectory


# 4. This class has close(), but no __enter__ or __exit__.
class Resource:
    def __init__(self):
        self.closed = False

    def use(self):
        print("Using resource.")

    def close(self):
        self.closed = True
        print("Resource closed.")


def main():
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source_path = root / "source.txt"
        target_path = root / "target.txt"
        source_path.write_text("Hello from a context manager!", encoding="utf-8")

        # 1. Two context managers in one with statement.
        # They are entered left to right and exited right to left.
        with open(source_path, encoding="utf-8") as source, open(
            target_path, "w", encoding="utf-8"
        ) as target:
            target.write(source.read())
        assert source.closed and target.closed
        print("Copied:", target_path.read_text(encoding="utf-8"))

        # 2. The list can contain any number of file paths (including zero).
        paths = [source_path, target_path]
        with ExitStack() as stack:
            files = [stack.enter_context(open(path, encoding="utf-8")) for path in paths]
            for file in files:
                print(file.name, "->", file.read())
        assert all(file.closed for file in files)
        # ExitStack also closes earlier files if opening a later file fails.

        # 3. Both versions ignore only FileNotFoundError.
        missing_file = root / "missing.txt"
        with suppress(FileNotFoundError):
            missing_file.unlink()

        try:
            missing_file.unlink()
        except FileNotFoundError:
            pass
        # suppress is shorter; try/except is useful for custom error handling.
        print("Missing file ignored by both versions.")

    # 4. closing calls close() on exit, including when an exception occurs.
    with closing(Resource()) as resource:
        resource.use()
    assert resource.closed


if __name__ == "__main__":
    main()
