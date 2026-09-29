import functools
import time

# --- @logged with functools.wraps ---
def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

# --- Version without functools.wraps ---
def logged_no_wraps(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

# Applying @logged to three functions
@logged
def add(a, b):
    """Adds two numbers."""
    return a + b

@logged
def greet(name):
    """Greets a person."""
    return f"Hello, {name}"

@logged
def multiply(a, b):
    """Multiplies two numbers."""
    return a * b

# --- @timer ---
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds")
        return result
    return wrapper

# --- @count_calls ---
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

if __name__ == "__main__":
    print("--- Demonstration of functools.wraps ---")
    print(f"WITH wraps    -> Name: {add.__name__}, Docstring: {add.__doc__}")
    
    @logged_no_wraps
    def sample_no_wraps():
        """Sample docstring without wraps."""
        pass
    print(f"WITHOUT wraps -> Name: {sample_no_wraps.__name__}, Docstring: {sample_no_wraps.__doc__}")

    print("\n--- Testing @logged on 3 functions ---")
    add(2, 3)
    greet("John")
    multiply(4, 5)

    print("\n--- Testing @timer ---")
    @timer
    def slow_func():
        time.sleep(0.1)
    slow_func()

    print("\n--- Testing @count_calls ---")
    @count_calls
    def say_hi():
        print("Hi!")

    say_hi()
    say_hi()
    say_hi()
    print(f"Total calls for say_hi: {say_hi.calls}")