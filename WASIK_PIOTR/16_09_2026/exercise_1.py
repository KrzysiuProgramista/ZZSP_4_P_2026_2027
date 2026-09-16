import functools
import time


def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result

    return wrapper


@logged
def add(a, b):
    """Add two numbers."""
    return a + b


@logged
def multiply(a, b):
    """Multiply two numbers."""
    return a * b


@logged
def greet(name):
    """Return a greeting."""
    return f"Hello, {name}!"


print(add.__name__)
print(add.__doc__)

print(add(2, 3))
print(multiply(4, 5))
print(greet("Python"))


def logged_without_wraps(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result

    return wrapper


@logged_without_wraps
def test_function():
    """This is a test function."""
    return "test"


print(test_function.__name__)
print(test_function.__doc__)


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds")
        return result

    return wrapper


@timer
def slow_function():
    time.sleep(0.2)
    return "finished"


print(slow_function())


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        return func(*args, **kwargs)

    wrapper.count = 0
    return wrapper


@count_calls
def square(x):
    return x * x


print(square(2))
print(square(3))
print(square(4))
print(f"square was called {square.count} times")