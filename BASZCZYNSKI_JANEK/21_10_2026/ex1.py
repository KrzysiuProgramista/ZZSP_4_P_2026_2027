import time
from types import SimpleNamespace
from contextlib import contextmanager


class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"took {self.elapsed:.3f}s")
        # The error is hiddent, makes the code harder to debug
        return exc_type is ValueError

with Timer() as timer:
    sum(i * i for i in range(100_000))

    a = int("dddawdg")


@contextmanager
def timer():
    result = SimpleNamespace(elapsed=None)
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed = time.perf_counter() - start
        print(f"took {result.elapsed:.3f}s")


with timer() as timing:
    sum(i * i for i in range(100_000))

print(timing.elapsed)
    