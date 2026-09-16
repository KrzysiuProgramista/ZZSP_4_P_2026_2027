import functools
import time

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} gave back {result!r}")
        return result
    return wrapper

def logged_without_wraps(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} gave back {result!r}")
        return result
    return wrapper

@logged
def add(a, b):
    """just adds two numbrs"""
    return a + b

@logged
def greet(name):
    """says hi to someon"""
    return f"hello {name}"

@logged
def multiply(a, b):
    """multiplis two numbers"""
    return a * b

@logged_without_wraps
def add_without_wraps(a, b):
    """adds two numbrs without wraps"""
    return a + b

print("testing loged with 3 functions")
add(3, 4)
greet("alice")
multiply(5, 6)

print("name and doc with wraps")
print(add.__name__)
print(add.__doc__)

print("name and doc without wraps")
print(add_without_wraps.__name__)
print(add_without_wraps.__doc__)

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        diff = end_time - start_time
        print(f"{func.__name__} took {diff} secnds")
        return result
    return wrapper

@timer
def count_big():
    total = 0
    for i in range(1000000):
        total = total + 1
    return total

print("testing timr")
count_big()

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.num_calls = wrapper.num_calls + 1
        return func(*args, **kwargs)
    wrapper.num_calls = 0
    return wrapper

@count_calls
def say_hi():
    print("hi")

print("testing count calss")
say_hi()
say_hi()
say_hi()
print(say_hi.num_calls)