
import time
from contextlib import contextmanager


class Timer:
    def __init__(self, label="Elapsed time"):
        self.label = label
        self.elapsed = None

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = time.perf_counter() - self.start
        print(f"{self.label}: {self.elapsed:.6f} seconds")

        if exc_type is ValueError:
            print("Suppressed ValueError")
            return True

        return False


@contextmanager
def timer(label="Elapsed time"):
    start = time.perf_counter()
    try:
        yield
    except ValueError:
        print("Suppressed ValueError")
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.6f} seconds")


with Timer("Class timer") as t1:
    time.sleep(0.1)

with timer("Generator timer"):
    time.sleep(0.1)


with Timer("Class timer with exception"):
    raise ValueError("Something went wrong")

with timer("Generator timer with exception"):
    raise ValueError("Something went wrong")


for context_manager in (
    lambda: Timer("Class timer"),
    lambda: timer("Generator timer"),
):
    try:
        with context_manager():
            raise TypeError("This exception must propagate")
    except TypeError as exc:
        print(f"Caught outside: {exc}")
