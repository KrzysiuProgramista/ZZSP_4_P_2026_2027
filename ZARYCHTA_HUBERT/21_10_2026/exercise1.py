from contextlib import contextmanager
from time import perf_counter, sleep


# 1. Class-based context manager
class Timer:
    def __enter__(self):
        self.start = perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = perf_counter() - self.start
        print(f"Elapsed: {self.elapsed:.4f} s")

        if exc_type is ValueError:
            # Suppressing exceptions is usually a bad idea because it hides
            # errors and lets the program continue with potentially invalid state.
            return True

        return False


# 2. Generator-based context manager
@contextmanager
def timer():
    result = {}
    start = perf_counter()

    try:
        yield result
    finally:
        result["elapsed"] = perf_counter() - start
        print(f"Elapsed: {result['elapsed']:.4f} s")


# 3. Both measure and report elapsed time.
with Timer() as class_timer:
    sleep(0.1)

with timer() as generator_timer:
    sleep(0.1)

assert class_timer.elapsed >= 0.1
assert generator_timer["elapsed"] >= 0.1
print("Both timers work correctly.")


# 4. ValueError is suppressed by Timer.__exit__ returning True.
with Timer():
    raise ValueError("This error will be suppressed.")

print("Execution continues.")