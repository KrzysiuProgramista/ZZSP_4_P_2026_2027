PRIMER ON PYTHON DECORATORS

Python decorators are a powerful and elegant way to modify or extend the
behavior of functions or methods without changing their actual code. This
document provides a summary of the concepts from the Real Python tutorial on
Python Decorators.

1.  FUNCTIONS ARE FIRST-CLASS OBJECTS

Before understanding decorators, you must understand that functions in Python
are first-class objects. This means that functions can be:

  - Assigned to a variable.
  - Passed as an argument to another function.
  - Returned from another function.
  - Defined inside another function (Inner Functions).

2.  WHAT IS A DECORATOR?

At its core, a decorator is a callable (a function) that takes another function
as an argument and extends its behavior without modifying it. It usually wraps
the original function inside an inner function.

The Syntactic Sugar (@) Instead of assigning the function manually (my_func =
my_decorator(my_func)), Python provides the @ symbol as a shortcut.

Example:

def my_decorator(func): def wrapper(): print("Something is happening before the
function is called.") func() print("Something is happening after the function is
called.") return wrapper

@my_decorator def say_whee(): print("Whee!")

say_whee()

Output: Something is happening before the function is called. Whee! Something is
happening after the function is called.

3.  DECORATING FUNCTIONS WITH ARGUMENTS

If you want your decorator to work on functions that take arguments, you must
use *args and **kwargs in the inner wrapper function.

Example:

def do_twice(func): def wrapper_do_twice(*args, **kwargs): func(*args, **kwargs)
return func(*args, **kwargs) return wrapper_do_twice

@do_twice def greet(name): print(f"Hello {name}")

greet("World")

(Note: The wrapper also needs to return the function call so that the decorated
function's return value is not lost!)

4.  PRESERVING FUNCTION IDENTITY

When a function is decorated, it is technically replaced by the wrapper
function. This means it loses its original name (name) and docstring (doc). To
prevent this, always use @functools.wraps on your wrapper function.

Example:

import functools

def my_decorator(func): @functools.wraps(func) def wrapper(*args, **kwargs): #
Do something before result = func(*args, **kwargs) # Do something after return
result return wrapper

5.  REAL-WORLD EXAMPLES

Decorators are highly reusable. Here are some common use cases:

  - @timer: Measures the execution time of a function.
  - @debug: Prints the arguments a function was called with and its return
    value.
  - @slow_down: Pauses the execution of a function for a certain amount of time
    (useful for rate-limiting).
  - @app.route: Used in web frameworks like Flask to register URLs to functions.

Example: A Timer Decorator

import functools import time

def timer(func): # Print the runtime of the decorated function
@functools.wraps(func) def wrapper_timer(*args, **kwargs): start_time =
time.perf_counter()
value = func(*args, **kwargs) end_time = time.perf_counter()
run_time = end_time - start_time
print(f"Finished {func.name!r} in {run_time:.4f} secs") return value return
wrapper_timer

@timer def waste_some_time(num_times): for _ in range(num_times): sum([i**2 for
i in range(10000)])

6.  ADVANCED DECORATORS

Decorators with Arguments Sometimes you want to pass arguments to your decorator
(e.g., @repeat(num_times=3)). This requires wrapping the decorator inside
another function (a decorator factory).

Example:

def repeat(num_times): def decorator_repeat(func): @functools.wraps(func) def
wrapper_repeat(*args, **kwargs): for _ in range(num_times): result = func(*args,
**kwargs) return result return wrapper_repeat return decorator_repeat

Classes as Decorators You can use a class as a decorator by implementing the
call() dunder method.

Example:

class CountCalls: def init(self, func): functools.update_wrapper(self, func)
self.func = func self.num_calls = 0

def __call__(self, *args, **kwargs):
    self.num_calls += 1
    print(f"Call {self.num_calls} of {self.func.__name__!r}")
    return self.func(*args, **kwargs)

Stateful Decorators Decorators can remember state from previous calls. The
CountCalls class above is a good example of a stateful decorator because it
remembers the number of times a function has been executed.