import functools
import time


def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Entering {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"[LOG] Exiting {func.__name__}")
        return result

    return wrapper


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[TIMER] Starting timer for {func.__name__}")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper


print("--- Defining slow_add_v1 (@logged over @timer) ---")


@logged
@timer
def slow_add_v1(a, b):
    time.sleep(0.05)
    return a + b


print("\nExecuting slow_add_v1(2, 3):")
slow_add_v1(2, 3)

print("\n--- Defining slow_add_v2 (@timer over @logged) ---")


@timer
@logged
def slow_add_v2(a, b):
    time.sleep(0.05)
    return a + b


print("\nExecuting slow_add_v2(2, 3):")
slow_add_v2(2, 3)