import functools
import time


# =====================================================================
# 1. Define the Two Decorators with Enter/Exit Prints
# =====================================================================
def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  [LOG ENTER] Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"  [LOG EXIT]  {func.__name__} returned {result}")
        return result
    return wrapper


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  [TIMER START] Measuring {func.__name__}...")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [TIMER END]   {func.__name__} completed in {elapsed:.4f}s")
        return result
    return wrapper


# =====================================================================
# Order 1: @logged on top of @timer
# Equivalent to: add_v1 = logged(timer(add_v1))
# =====================================================================
print("=" * 65)
print("ORDER 1: @logged on top, @timer on bottom")
print("Equivalent to: add_v1 = logged(timer(add_v1))")
print("=" * 65)

@logged
@timer
def slow_add_v1(a, b):
    print("    --> Inside core slow_add_v1()")
    time.sleep(0.05)
    return a + b

print("\nExecuting slow_add_v1(2, 3):")
res1 = slow_add_v1(2, 3)
print(f"Final output: {res1}\n")


# =====================================================================
# Order 2: Swapping the order -> @timer on top of @logged
# Equivalent to: add_v2 = timer(logged(add_v2))
# =====================================================================
print("=" * 65)
print("ORDER 2: @timer on top, @logged on bottom")
print("Equivalent to: add_v2 = timer(logged(add_v2))")
print("=" * 65)

@timer
@logged
def slow_add_v2(a, b):
    print("    --> Inside core slow_add_v2()")
    time.sleep(0.05)
    return a + b

print("\nExecuting slow_add_v2(5, 7):")
res2 = slow_add_v2(5, 7)
print(f"Final output: {res2}\n")


# =====================================================================
# Key Observation Summary
# =====================================================================
print("=" * 65)
print("KEY TAKEAWAY ON ORDERING:")
print("=" * 65)
print("""
In Order 1 (@logged -> @timer):
  1. [LOG ENTER] runs first.
  2. [TIMER START] runs second.
  3. Function runs.
  4. [TIMER END] records time for ONLY the function.
  5. [LOG EXIT] runs last.
  -> Logging is OUTSIDE; the timer does NOT measure logging overhead.

In Order 2 (@timer -> @logged):
  1. [TIMER START] runs first.
  2. [LOG ENTER] runs second.
  3. Function runs.
  4. [LOG EXIT] runs.
  5. [TIMER END] runs last.
  -> The timer is OUTSIDE; it measures the function AND the logging overhead!
""")