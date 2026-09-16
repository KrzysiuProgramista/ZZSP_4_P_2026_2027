# In order to understand decorators, you must first understand some finer points of how functions work. 
  - Basic Functions
  - Nested Functions (Inner Functions)
  - First-Class Functions
  - Closures

# What Are Decorators?
A decorator is a design pattern in Python that allows a user to add new functionality to an existing object without modifying its structure.

Simply put: Decorators wrap a function, modifying its behavior.

Here is a manual implementation of a decorator:

Python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

def say_whee():
    print("Whee!")

say_whee = my_decorator(say_whee)
say_whee()
Output:

Something is happening before the function is called.
Whee!
Something is happening after the function is called.

# Decorating Functions with Arguments
If the decorated function takes arguments, your wrapper function must accept them too! You can use *args and **kwargs to make your decorators universal.

Python
def do_twice(func):
    def wrapper_do_twice(*args, **kwargs):
        func(*args, **kwargs)
        func(*args, **kwargs)
    return wrapper_do_twice

@do_twice
def greet(name):
    print(f"Hello {name}")

greet("World")

Output:

Hello World
Hello World

# Returning Values from Decorated Functions
To ensure your decorator doesn't break functions that return values, the wrapper function must return the result of the decorated function call.

Python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("Doing something before.")
        result = func(*args, **kwargs)
        print("Doing something after.")
        return result  # Crucial!
    return wrapper

@my_decorator
def return_greeting(name):
    print("Creating greeting...")
    return f"Hi {name}"

print(return_greeting("Alice"))

# The Mystery of functools.wraps
When you decorate a function, it loses its original identity (__name__ and __doc__ become those of the wrapper). To fix this, use functools.wraps.

# Common Practical Decorators
Timing Functions (@timer)
Measure how long a function takes to execute.

Python
import functools
import time

def timer(func):
    """Print the runtime of the decorated function"""
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer

@timer
def waste_time(num):
    for _ in range(num):
        sum([i**2 for i in range(1000)])

waste_time(999)
Debugging Code (@debug)
Print arguments and return values every time a function is called.

Python
import functools

def debug(func):
    """Print the function signature and return value"""
    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {value!r}")
        return value
    return wrapper_debug

@debug
def make_greeting(name, age=None):
    if age is None:
        return f"Howdy {name}!"
    return f"Whoa {name}! {age} already?"

make_greeting("Ben", age=29)

# Stateful Decorators (Decorators with Classes)
Sometimes you need a decorator to maintain state (e.g., counting how many times a function has been called). You can implement this by turning the decorator into a class.

# Nested Decorators (Stacking)
You can apply multiple decorators to a single function by stacking them. They are applied from bottom to top (closest to the function first).

Python
def uppercase(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper()
    return wrapper

def split_string(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).split()
    return wrapper

@split_string
@uppercase
def greet():
    return "hello world"

print(greet())  # Output: ['HELLO', 'WORLD']