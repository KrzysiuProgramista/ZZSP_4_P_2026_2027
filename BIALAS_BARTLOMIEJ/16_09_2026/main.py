import functools
import time


# ---------------------------------------------------------------------------
# 1.1 — @logged
# ---------------------------------------------------------------------------
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
def greet(name):
    """Return a greeting for name."""
    return f"Hello, {name}!"


@logged
def square(n):
    """Return n squared."""
    return n * n


# ---------------------------------------------------------------------------
# 1.2 — __name__ / __doc__ with vs without functools.wraps
# ---------------------------------------------------------------------------
def logged_no_wraps(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@logged_no_wraps
def add_broken(a, b):
    """Add two numbers."""
    return a + b


# ---------------------------------------------------------------------------
# 1.3 — @timer
# ---------------------------------------------------------------------------
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper


@timer
def slow_add(a, b):
    time.sleep(0.2)
    return a + b


# ---------------------------------------------------------------------------
# 1.4 — @count_calls
# ---------------------------------------------------------------------------
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def ping():
    return "pong"


# ---------------------------------------------------------------------------
# Run everything and print results
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== 1.1 @logged on three functions ===")
    add(2, 3)
    greet("Ada")
    square(5)

    print("\n=== 1.2 __name__ / __doc__ ===")
    print("WITH functools.wraps:")
    print(f"  add.__name__ = {add.__name__!r}")
    print(f"  add.__doc__  = {add.__doc__!r}")

    print("WITHOUT functools.wraps:")
    print(f"  add_broken.__name__ = {add_broken.__name__!r}  (lost, shows 'wrapper')")
    print(f"  add_broken.__doc__  = {add_broken.__doc__!r}  (lost, shows None)")

    print("\n=== 1.3 @timer ===")
    slow_add(1, 2)

    print("\n=== 1.4 @count_calls ===")
    ping()
    ping()
    ping()
    print(f"ping.calls = {ping.calls}")