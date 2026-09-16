import functools
import time

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"-> Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} returned {result!r}")
        return result
    return wrapper

def logged_without_wraps(func):
    def wrapper(*args, **kwargs):
        print(f"-> Calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"<- {func.__name__} returned {result!r}")
        return result
    return wrapper

@logged
def add(a, b):
    """Adds two numbers together."""
    return a + b

@logged
def multiply(a, b):
    """Multiplies two numbers."""
    return a * b

@logged
def greet(name):
    """Greets a user by name."""
    return f"Hello, {name}!"

print("WITH @functools.wraps:")
print("Name:", add.__name__)
print("Docstring:", add.__doc__)

@logged_without_wraps
def sample_func():
    """This is a sample docstring."""
    pass

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"⏱️ '{func.__name__}' executed in {duration:.6f} seconds.")
        return result
    return wrapper

@timer
def heavy_calculation(n):
    return sum(i**2 for i in range(n))

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.call_count += 1
        print(f"🔢 '{func.__name__}' has been called {wrapper.call_count} time(s).")
        return func(*args, **kwargs)
    
    wrapper.call_count = 0
    return wrapper

@count_calls
def say_hello():
    print("Hello!")

say_hello()
say_hello()
say_hello()

print("\nWITHOUT @functools.wraps:")
print("Name:", sample_func.__name__)  # This will output 'wrapper' instead of 'sample_func'
print("Docstring:", sample_func.__doc__) # This will be None!

heavy_calculation(1_000_000)

print(f"Final count check via attribute: {say_hello.call_count}")