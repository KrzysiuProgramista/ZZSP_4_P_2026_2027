import functools
import inspect
import time


def logged(func):
    """Print a function's name before its call and its result afterwards."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result

    return wrapper


def timer(func):
    """Report elapsed seconds, even if the wrapped call raises an exception."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        started = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - started
            print(f"{func.__name__} took {elapsed:.6f} seconds")

    return wrapper


def count_calls(func):
    """Expose the number of attempted calls as the wrapper's .calls attribute."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


def logged_without_wraps(func):
    """Deliberately omit wraps for the required metadata comparison only."""
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result

    return wrapper


@logged
def add(a, b):
    """Return a plus b."""
    return a + b


@logged
def multiply(a, b):
    """Return a multiplied by b."""
    return a * b


@logged
def greet(name="world"):
    """Build a greeting for the given name."""
    return f"Hello, {name}!"


@timer
def sum_of_squares(limit):
    """Add the squares of integers from zero up to, but excluding, limit."""
    return sum(number * number for number in range(limit))


@count_calls
def square(number):
    """Return the square of a number."""
    return number * number


def compare_add_metadata(original_add):
    """Wrap the same original add twice and display both sets of metadata."""
    add = logged(original_add)
    print("\nWith functools.wraps:")
    print("add.__name__:", add.__name__)
    print("add.__doc__:", add.__doc__)
    print("inspect.signature(add):", inspect.signature(add))

    add = logged_without_wraps(original_add)
    print("\nWithout functools.wraps (demonstration only):")
    print("add.__name__:", add.__name__)
    print("add.__doc__:", add.__doc__)
    print("inspect.signature(add):", inspect.signature(add))


def main():
    print("1. Logging three functions:")
    add(4, 7)
    multiply(a=3, b=5)
    greet("Hubert")

    print("\n2. Comparing metadata:")
    # wraps exposes the undecorated function through __wrapped__.
    compare_add_metadata(add.__wrapped__)

    print("\n3. Measuring execution time:")
    print("Result:", sum_of_squares(100_000))

    print("\n4. Counting calls:")
    print("square.calls before:", square.calls)
    for number in (2, 3, 4):
        print(f"square({number}) = {square(number)}")
    print("square.calls after:", square.calls)


if __name__ == "__main__":
    main()
