import functools
import time

def logged(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

def timer(func):
    def wrapper(*args, **kwargs):
        pre = time.time()
        result = func(*args, **kwargs)
        post = time.time()
        print(f"Function {func.__name__} took {post-pre}ms")
        return result
    return wrapper

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    
    wrapper.calls = 0
    return wrapper

@timer
@logged
def add(a, b):
    time.sleep(0.1)

    return a + b

@count_calls
@logged
def substract(a, b):
    return a - b

@logged
def multiply(a,b):
    return a*b

add(1, 2)
substract(2, 3)
multiply(13, 3)

substract(1,1)
substract(1,1)
substract(1,1)

print(f"Function substact was called: {substract.calls} times")