import time
from types import SimpleNamespace
from contextlib import contextmanager

class Timer:
    def __init__(self):
        self.result = SimpleNamespace(elapsed=None)
        self.start = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.result.elapsed = time.perf_counter() - self.start
        print(f"[Class Timer] took {self.result.elapsed:.3f}s")
        
        if exc_type is ValueError:

            return True

        return False

@contextmanager
def timer_gen():
    result = SimpleNamespace(elapsed=None)
    start = time.perf_counter()
    try:
        yield result
    finally:
        result.elapsed = time.perf_counter() - start
        print(f"[Generator Timer] took {result.elapsed:.3f}s")



print("--- Testing Class-based Timer ---")
with Timer() as timing:
    sum(i * i for i in range(100_000))
print(f"Elapsed retrieved: {timing.elapsed:.5f}s\n")

print("--- Testing Generator-based Timer ---")
with timer_gen() as timing_g:
    sum(i * i for i in range(100_000))
print(f"Elapsed retrieved: {timing_g.elapsed:.5f}s\n")

print("--- Testing Exception Suppression (Class Timer) ---")
try:
    with Timer() as t:
        print("Inside block: about to raise ValueError")
        raise ValueError("Something went wrong inside the block!")
    print("Inside block: this line executes because ValueError was suppressed!")
except ValueError:
    print("Exception caught by outer try/except (this won't print because it was suppressed).")