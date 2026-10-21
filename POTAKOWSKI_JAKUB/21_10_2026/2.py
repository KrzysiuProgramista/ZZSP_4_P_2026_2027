import time
from contextlib import contextmanager


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.6f} seconds")
        return False


@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Elapsed: {elapsed:.6f} seconds")


with Timer() as t:
    time.sleep(0.1)

print(f"Measured: {t.elapsed:.6f} seconds")

with timer():
    time.sleep(0.1)


class SuppressValueError:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is ValueError:
            # Suppressing exceptions can hide bugs and make them difficult to diagnose.
            return True
        return False


with SuppressValueError():
    raise ValueError("Something went wrong")

print("Execution continues.")