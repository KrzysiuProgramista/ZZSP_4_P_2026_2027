import time
from types import SimpleNamespace
from contextlib import contextmanager

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        print(f"[Class Timer] took {self.elapsed:.3f}s")
        
        if exc_type is ValueError:
            print(f"[Class Timer] Suppressed ValueError: {exc}")
            
            # Why silent suppressing is bad idea:
            # - Hides bugs.
            # - Breaks control flow.
            # - Violates Single Responsibility Principle.
            
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

if __name__ == "__main__":
    print("--- 1. Testing Class Timer (Normal Execution) ---")
    with Timer() as timing_class:
        sum(i * i for i in range(100_000))
    print(f"Elapsed attribute: {timing_class.elapsed:.3f}s\n")

    print("--- 2. Testing Generator Timer (Normal Execution) ---")
    with timer_gen() as timing_gen:
        sum(i * i for i in range(100_000))
    print(f"Elapsed attribute: {timing_gen.elapsed:.3f}s\n")

    print("--- 3. Testing Exception Suppression (Class Timer) ---")
    with Timer() as timing_suppressed:
        raise ValueError("An intentional error occurred inside the block!")
    print("Execution successfully continued past the 'with' block because ValueError was suppressed!")