import time
from contextlib import contextmanager

class TimerClass:
    def __enter__(self):
        self.start = time.time()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Class Timer:", time.time() - self.start)
        return True

@contextmanager
def timer_gen():
    start = time.time()
    try:
        yield
    finally:
        print("Generator Timer:", time.time() - start)

with TimerClass():
    time.sleep(0.1)
    raise ValueError("test")
print("Exception was suppressed")

with timer_gen():
    time.sleep(0.1)