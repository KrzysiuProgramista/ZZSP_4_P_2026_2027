import time
from contextlib import contextmanager


class TimerClass:

  def __init__(self, suppress_exc=None):
    self.suppress_exc = suppress_exc
    self.elapsed = 0.0

  def __enter__(self):
    self.start_time = time.perf_counter()
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.elapsed = time.perf_counter() - self.start_time
    print(f"[Class Timer] Elapsed time: {self.elapsed:.4f} seconds")

    # 4. Make one of them suppress a specific exception
    if exc_type and issubclass(exc_type, self.suppress_exc):
      # 5. Why this is usually a bad idea:
      # Suppressing exceptions silently swallows errors (like typos, KeyErrors,
      # or unintended bugs) inside the block. This makes debugging extremely
      # difficult because the program continues execution as if nothing failed.
      return True

    return False  # Propagate other exceptions normally



@contextmanager
def timer_generator():
  start_time = time.perf_counter()
  try:
    yield
  finally:
    elapsed = time.perf_counter() - start_time
    print(f"[Generator Timer] Elapsed time: {elapsed:.4f} seconds")

    # --- Testing Normal Behavior ---
print("--- Testing Class Timer ---")
with TimerClass() as t:
  time.sleep(0.1)

print("\n--- Testing Generator Timer ---")
with timer_generator():
  time.sleep(0.1)

# --- Testing Exception Suppression (Class Timer) ---
print("\n--- Testing Exception Suppression ---")
with TimerClass(suppress_exc=ValueError):
  print("Inside block: about to raise ValueError")
  raise ValueError("Something went wrong!")

print("Program survived the suppressed exception!")