import functools
import time

# ==========================================
# Part 1 & 2: @logged and __wraps__ comparison
# ==========================================

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

def logged_unwrapped(func):
    # Without functools.wraps
    def wrapper(*args, **kwargs):
        print(f"Calling function")
        return func(*args, **kwargs)
    return wrapper

# Applying @logged to three functions
@logged
def add(a, b):
    """Adds two numbers together."""
    return a + b

@logged
def multiply(a, b):
    """Multiplies two numbers together."""
    return a * b

@logged
def power(base, exp):
    """Raises base to the power of exp."""
    return base ** exp

# Comparing with and without wraps
def sample_func(x):
    """A sample docstring."""
    return x

wrapped_version = logged(sample_func)
unwrapped_version = logged_unwrapped(sample_func)

print("--- With @functools.wraps ---")
print("Name:", wrapped_version.__name__)
print("Docstring:", wrapped_version.__doc__)

print("\n--- Without @functools.wraps ---")
print("Name:", unwrapped_version.__name__)
print("Docstring:", unwrapped_version.__doc__)

# ==========================================
# Part 3: @timer decorator
# ==========================================

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"-> '{func.__name__}' took {elapsed_time:.6f} seconds to execute.")
        return result
    return wrapper

@timer
def compute_heavy_task(n):
    """Simulates a heavy computation."""
    return sum(i**2 for i in range(n))

# ==========================================
# Part 4: @count_calls decorator
# ==========================================

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        print(f"-> '{func.__name__}' has been called {wrapper.call_count} time(s).")
        return func(*args, **kwargs)
    wrapper.call_count = 0
    return wrapper

@count_calls
def say_hello(name):
    """Greets a user."""
    return f"Hello, {name}!"

# ==========================================
# Testing everything out
# ==========================================
if __name__ == "__main__":
    print("\n=== Testing @logged ==/")
    add(3, 5)

    print("\n=== Testing @timer ==/")
    compute_heavy_task(100_000)

    print("\n=== Testing @count_calls ==/")
    say_hello("Alice")
    say_hello("Bob")
    say_hello("Charlie")
    print(f"Total calls tracked via attribute: {say_hello.call_count}")