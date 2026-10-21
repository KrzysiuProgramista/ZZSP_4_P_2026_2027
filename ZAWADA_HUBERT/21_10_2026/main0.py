import contextlib
import time


class TimerClass:

  def __init__(self, suppress_exc=False):
    self.suppress_exc = suppress_exc
    self.start = None
    self.elapsed = None

  def __enter__(self):
    self.start = time.perf_counter()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.elapsed = time.perf_counter() - self.start
    if exc_type is not None and self.suppress_exc:
      return True
    return False


@contextlib.contextmanager
def timer_generator():
  start = time.perf_counter()
  try:
    yield
  finally:
    elapsed = time.perf_counter() - start
    print(f"Generator Timer elapsed: {elapsed:.6f} seconds")


if __name__ == "__main__":
  with TimerClass() as t1:
    time.sleep(0.1)
  print(f"Class Timer elapsed: {t1.elapsed:.6f} seconds")

  with timer_generator():
    time.sleep(0.1)

  with TimerClass(suppress_exc=True):
    raise ValueError("Test exception")
  print("Execution continued because the exception was suppressed.")