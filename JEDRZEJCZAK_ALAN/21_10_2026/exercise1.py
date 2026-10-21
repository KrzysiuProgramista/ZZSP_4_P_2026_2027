
import time
from contextlib import contextmanager


# 1. Timer as a class
class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self.start
        print(f"Class Timer: {elapsed:.4f} seconds")
        return False


# 2. Timer as a generator
@contextmanager
def timer():
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"Generator Timer: {elapsed:.4f} seconds")


# 3. Test both versions
print("Testing class Timer:")
with Timer():
    time.sleep(1)

print("Testing generator Timer:")
with timer():
    time.sleep(1)


# 4. Suppress a specific exception
class SafeTimer(Timer):
    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)

        if exc_type is ValueError:
            print("ValueError suppressed")
            return True

        return False


print("Testing exception suppression:")
with SafeTimer():
    raise ValueError("Test error")

print("Program continues normally.")
