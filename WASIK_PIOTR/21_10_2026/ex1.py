
import time
from contextlib import contextmanager


# 1. Timer implemented as a class-based context manager
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.elapsed = time.perf_counter() - self.start
        print(f"Elapsed time: {self.elapsed:.6f} seconds")
        return False


# 2. The same Timer implemented as a @contextmanager generator
@contextmanager
def timer():
    result = {}

    start = time.perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = time.perf_counter() - start
        print(f"Elapsed time: {result['elapsed']:.6f} seconds")


# 3. Use both context managers and compare their behavior
print("Class-based Timer:")
with Timer() as class_timer:
    time.sleep(0.1)

print("Measured:", f"{class_timer.elapsed:.6f} seconds")

print("\nGenerator-based Timer:")
with timer() as generator_timer:
    time.sleep(0.1)

print("Measured:", f"{generator_timer['elapsed']:.6f} seconds")


# Confirm that both context managers propagate exceptions
print("\nChecking exception propagation:")

try:
    with Timer():
        raise ValueError("Test exception")
except ValueError:
    print("Class-based Timer propagated ValueError.")

try:
    with timer():
        raise ValueError("Test exception")
except ValueError:
    print("Generator-based Timer propagated ValueError.")


# 4. Suppress a specific exception by returning True from __exit__
class SuppressingTimer(Timer):
    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

        if exc_type is ValueError:
            # Suppressing exceptions is usually a bad idea because it can
            # hide bugs and prevent the caller from detecting failures.
            return True

        return False


print("\nSuppressing a specific exception:")
with SuppressingTimer():
    raise ValueError("This ValueError will be suppressed.")

print("Execution continues after the suppressed ValueError.")

