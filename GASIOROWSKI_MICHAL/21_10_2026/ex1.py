import time
from types import SimpleNamespace
from contextlib import contextmanager

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"Took {self.elapsed:.3f}s")
        return exc_type is ValueError

@contextmanager
def timer():
    result = SimpleNamespace(elasped=None)
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed = time.perf_counter() - start
        print(f"Took {result.elapsed:.3f}s")

with timer() as timing:
    sum(i * i for i in range(100_00))

with Timer() as timer:
    sum(i * i for i in range(100_000))
    # This is a bad idea because hiding and suppressing errors
    # makes us ignore problems, which while may seem at the moment
    # trivial or not harmful, can potentially become problematic
    # later on
    raise ValueError

print(timer.elapsed)
print(timing.elapsed)
