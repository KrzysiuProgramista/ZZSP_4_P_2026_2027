"""
Exercise 6: Stacking decorators
"""
import functools
import time


def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[logged]  entering {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[logged]  leaving {func.__name__} -> {result}")
        return result
    return wrapper


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[timer]   starting timer for {func.__name__}")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer]   {func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper



@logged
@timer
def slow_add(a, b):
    time.sleep(0.01)
    return a + b

@timer
@logged
def slow_add_swapped(a, b):
    time.sleep(0.01)
    return a + b


if __name__ == "__main__":
    print("-- original order: @logged / @timer --")
    slow_add(2, 3)

    print("\n-- swapped order: @timer / @logged --")
    slow_add_swapped(2, 3)
