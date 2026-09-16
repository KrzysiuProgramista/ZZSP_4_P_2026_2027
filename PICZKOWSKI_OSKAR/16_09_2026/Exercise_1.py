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



print("=== LOGGED ===")

print(add(2, 3))
print(multiply(4, 5))
print(greet("Alice"))


def logged_without_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def logged_with_wraps(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@logged_without_wraps
def test_without_wraps():
    """This is the original docstring."""
    pass


@logged_with_wraps
def test_with_wraps():
    """This is the original docstring."""
    pass


print()
print("=== WITHOUT functools.wraps ===")

print("Name:", test_without_wraps.__name__)
print("Doc:", test_without_wraps.__doc__)


print()
print("=== WITH functools.wraps ===")

print("Name:", test_with_wraps.__name__)
print("Doc:", test_with_wraps.__doc__)


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()

        result = func(*args, **kwargs)

        elapsed = time.perf_counter() - start

        print(f"{func.__name__} took {elapsed:.6f} seconds")

        return result

    return wrapper


@timer
def slow_function():
    """A function that takes some time."""
    time.sleep(1)
    return "Done!"


print()
print("=== TIMER ===")

result = slow_function()
print(result)


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        return func(*args, **kwargs)

    wrapper.count = 0

    return wrapper


@count_calls
def say_hello(name):
    """Say hello to someone."""
    return f"Hello, {name}!"


print()
print("=== COUNT CALLS ===")

print(say_hello("Alice"))
print(say_hello("Bob"))
print(say_hello("Charlie"))

print("Function was called:", say_hello.count, "times")