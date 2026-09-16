# Python Decorators

## What is a decorator?

A decorator is a function that takes another function as an argument and returns a new function.

Decorators allow us to add functionality to an existing function without changing its source code.

Basic example:

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result
    return wrapper
```

## The `@` syntax

Python provides special syntax for applying decorators:

```python
@logged
def add(a, b):
    return a + b
```

This is equivalent to:

```python
def add(a, b):
    return a + b

add = logged(add)
```

Therefore, `@logged` is another way of writing:

```python
add = logged(add)
```

## Inner functions

A decorator commonly contains an inner function called a wrapper.

```python
def decorator(func):
    def wrapper(*args, **kwargs):
        print("Before")
        result = func(*args, **kwargs)
        print("After")
        return result

    return wrapper
```

The wrapper can execute code before and after the original function.

Using `*args` and `**kwargs` allows the wrapper to accept different positional and keyword arguments.

## `functools.wraps`

When creating decorators, `functools.wraps(func)` should be used on the wrapper.

```python
import functools

def decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper
```

`functools.wraps` preserves important information about the original function, including its name and docstring.

For example:

```python
@decorator
def add(a, b):
    """Add two numbers."""
    return a + b

print(add.__name__)
print(add.__doc__)
```

With `functools.wraps`, the output is:

```text
add
Add two numbers.
```

Without `functools.wraps`, the wrapper can appear as the decorated function:

```text
wrapper
None
```

This is important for debugging, documentation, `help()`, and frameworks that inspect functions.

## Logging decorator

A decorator can be used to log function calls.

```python
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result

    return wrapper
```

Example:

```python
@logged
def add(a, b):
    return a + b
```

Calling:

```python
add(2, 3)
```

can produce:

```text
calling add
add returned 5
```

## Timing decorator

Decorators can also be used to measure how long a function takes to execute.

Python provides `time.perf_counter()` for measuring elapsed time.

```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()

        print(f"{func.__name__} took {end - start:.6f} seconds")

        return result

    return wrapper
```

Example:

```python
@timer
def slow_function():
    time.sleep(0.2)
```

## Stateful decorators

A decorator can keep track of information between function calls.

For example, a decorator can count how many times a function has been called:

```python
import functools

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.count += 1
        return func(*args, **kwargs)

    wrapper.count = 0
    return wrapper
```

Example:

```python
@count_calls
def square(x):
    return x * x

square(2)
square(3)
square(4)

print(square.count)
```

Output:

```text
3
```

The count is stored as an attribute of the wrapper function.

## Multiple decorators

A function can have more than one decorator.

```python
@timer
@logged
def add(a, b):
    return a + b
```

This is equivalent to:

```python
add = timer(logged(add))
```

The order of decorators matters because one decorator wraps the result of another decorator.

## Common uses of decorators

Decorators are commonly used for:

* logging
* measuring execution time
* counting function calls
* caching results
* validating arguments
* authentication and authorization
* registering functions
* adding debugging functionality

## Summary

A decorator:

1. Takes a function.
2. Defines or creates a wrapper.
3. Adds additional behavior.
4. Returns the wrapper.

The `@decorator` syntax is shorthand for assigning the decorated function back to its original name.

Always use:

```python
@functools.wraps(func)
```

when writing decorators so that important metadata from the original function is preserved.

## Source

Based on and adapted from:

**Real Python — Primer on Python Decorators**

https://realpython.com/primer-on-python-decorators/
