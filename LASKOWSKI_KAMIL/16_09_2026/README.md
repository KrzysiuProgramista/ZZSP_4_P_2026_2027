1. Decorating Functions with Arguments
To write a decorator that can handle functions with any number of arguments, use *args and **kwargs in the inner wrapper function:

Python
import functools

def do_twice(func):
    @functools.wraps(func)
    def wrapper_do_twice(*args, **kwargs):
        func(*args, **kwargs)
        return func(*args, **kwargs)
    return wrapper_do_twice

@do_twice
def greet(name):
    print(f"Hello {name}")

greet("World")
2. Real-World Examples
Timing Functions (@timer)
A common use case for decorators is measuring the execution time of functions [cite: 1.1.5, 1.1.8]:

Python
import functools
import time

def timer(func):
    \"\"\"Print the runtime of the decorated function\"\"\"
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
def waste_some_time(num_times):
    for _ in range(num_times):
        sum([i**2 for i in range(10000)])
3. Advanced Decorators
Nesting Decorators: You can apply multiple decorators to a single function by stacking them. They are executed from bottom to top (closest to the function definition first).

Decorators with Arguments: To pass arguments to a decorator itself, you need to write a decorator factory (a function that returns a decorator).

Stateful Decorators: Decorators can maintain state across calls using function attributes or classes.

Classes as Decorators: Instead of functions, classes can also be used as decorators by implementing the __call__ special method.