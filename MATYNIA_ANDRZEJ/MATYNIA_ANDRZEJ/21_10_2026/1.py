import time
from contextlib import contextmanager


class Timer:

  def __init__(self, name="Timer"):
    self.name = name
    self.start_time = None
    self.elapsed = 0

  def __enter__(self):
    self.start_time = time.perf_counter()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.elapsed = time.perf_counter() - self.start_time
    print(f"[{self.name}] Elapsed time: {self.elapsed:.6f} seconds")

    if exc_type is ValueError:
      # returning true silently swallows the exception and this is dangerous because it can hide actual bugs or invalid state 
      # or unexpected failures in your block making debugging extremely difficult since the program continues
      # as if nothing went wrong
      print(f"Suppressed exception: {exc_val}")
      return True

    return False

  from contextlib import contextmanager
import time


@contextmanager
def timer_generator(name="Timer"):
  start_time = time.perf_counter()
  try:
    yield
  finally:
    elapsed = time.perf_counter() - start_time
    print(f"[{name}] Elapsed time: {elapsed:.6f} seconds")

if __name__ == "__main__":
  print("--- Testing class based timer ---")
  with Timer("Class timer"):
    time.sleep(0.1)

  print("\n--- Testing generator based timer ---")
  with timer_generator("Generator timer"):
    time.sleep(0.1)

  print("\n--- Testing exception suppression (Class based) ---")
  with Timer("Suppression timer"):
    print("Doing some work...")
    raise ValueError("Invalid value encountered")

  print(
      "Program successfully continued execution because the ValueError was suppressed"
  )
