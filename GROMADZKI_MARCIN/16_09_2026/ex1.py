import functools
import time

# ==========================================
# 1. @logged WITH and WITHOUT functools.wraps
# ==========================================

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

def logged_no_wraps(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

@logged
def add(a, b):
    """Adds two numbers and returns the sum."""
    return a + b

@logged
def multiply(a, b):
    """Multiplies two numbers."""
    return a * b

@logged
def greet(name):
    """Returns a greeting string."""
    return f"Hello, {name}!"

@logged_no_wraps
def add_no_wraps(a, b):
    """Adds two numbers (but loses metadata because of missing wraps)."""
    return a + b


print("--- DEMONSTRATING __name__ AND __doc__ ---")
print("WITH functools.wraps:")
print(f"Name: {add.__name__}")
print(f"Doc:  {add.__doc__}")

print("\nWITHOUT functools.wraps:")
print(f"Name: {add_no_wraps.__name__}")
print(f"Doc:  {add_no_wraps.__doc__}")
print("-" * 40, "\n")


# ==========================================
# 2. @timer Decorator
# ==========================================
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.6f} seconds to execute.")
        return result
    return wrapper

@timer
def slow_greeting(name):
    """Simulates a slow function."""
    time.sleep(1)
    return f"Slow hello to {name}"

print("--- TESTING @timer ---")
slow_greeting("Bob")
print("-" * 40, "\n")


# ==========================================
# 3. @count_calls Decorator
# ==========================================
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        return func(*args, **kwargs)
    
    wrapper.call_count = 0
    return wrapper

@count_calls
def roll_dice():
    """Simulates rolling a die."""
    return 4

print("--- TESTING @count_calls ---")
roll_dice()
roll_dice()
roll_dice()
print(f"roll_dice was called {roll_dice.call_count} times.")
print("-" * 40)