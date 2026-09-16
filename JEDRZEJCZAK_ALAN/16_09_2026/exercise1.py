"""
Exercise 1: First decorators

1. @logged applied to three functions.
2. add.__name__ / add.__doc__ with and without functools.wraps.
3. @timer prints how long a function took.
4. @count_calls tracks how many times a function was called and exposes
   the count as an attribute on the wrapper.
"""

import functools
import time



def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[logged] Calling {func.__name__}(args={args}, kwargs={kwargs})")
        result = func(*args, **kwargs)
        print(f"[logged] {func.__name__} returned {result!r}")
        return result
    return wrapper


@logged
def add(a, b):
    """Return the sum of a and b."""
    return a + b


@logged
def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"


@logged
def square(x):
    """Return x squared."""
    return x * x



def logged_no_wraps(func):
    # No functools.wraps here -> metadata gets lost.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def logged_with_wraps(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@logged_no_wraps
def add_no_wraps(a, b):
    """Return the sum of a and b."""
    return a + b


@logged_with_wraps
def add_with_wraps(a, b):
    """Return the sum of a and b."""
    return a + b



def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.6f} seconds")
        return result
    return wrapper


@timer
def slow_sum(n):
    """Sum numbers from 0 to n-1 the slow way."""
    total = 0
    for i in range(n):
        total += i
    return total



def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def say_hi():
    """Print a friendly greeting."""
    print("Hi!")


if __name__ == "__main__":
    print("=" * 60)
    print("1. @logged applied to three functions")
    print("=" * 60)
    add(2, 3)
    greet("Ada")
    square(5)

    print()
    print("=" * 60)
    print("2. __name__ / __doc__ with and without functools.wraps")
    print("=" * 60)
    print("Without functools.wraps:")
    print("  add_no_wraps.__name__ =", add_no_wraps.__name__)
    print("  add_no_wraps.__doc__  =", add_no_wraps.__doc__)
    print("With functools.wraps:")
    print("  add_with_wraps.__name__ =", add_with_wraps.__name__)
    print("  add_with_wraps.__doc__  =", add_with_wraps.__doc__)

    print()
    print("=" * 60)
    print("3. @timer")
    print("=" * 60)
    slow_sum(1_000_000)

    print()
    print("=" * 60)
    print("4. @count_calls")
    print("=" * 60)
    say_hi()
    say_hi()
    say_hi()
    print(f"say_hi was called {say_hi.calls} times")
