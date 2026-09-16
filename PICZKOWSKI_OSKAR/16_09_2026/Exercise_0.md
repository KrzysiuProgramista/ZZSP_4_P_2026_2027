# Exercise 0 — Python Decorators

Decorators are a Python feature used to **extend or modify the behavior of a function without changing the function itself**.

A decorator is a function that takes another function as an argument and returns a new function, usually called a wrapper.

## Basic decorator

A simple decorator can execute additional code before and after the original function:

```python
from functools import wraps

def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)

    return wrapper


@log_call
def greet(name):
    print(f"Hello, {name}!")


greet("Alice")
```

The `@log_call` syntax is shorthand for:

```python
greet = log_call(greet)
```

The original `greet()` function is passed to the decorator, and the returned wrapper replaces it.

## `*args` and `**kwargs`

Using `*args` and `**kwargs` makes the decorator reusable with functions that accept different arguments.

```python
def log_call(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)

    return wrapper
```

`*args` stores positional arguments, while `**kwargs` stores keyword arguments.

## Decorators with arguments

A decorator can also accept its own arguments. This requires an additional function level:

```python
from functools import wraps

def repeat(n):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None

            for _ in range(n):
                result = func(*args, **kwargs)

            return result

        return wrapper

    return decorator
```

Usage:

```python
@repeat(3)
def hello():
    print("Hello!")


hello()
```

The function will be executed three times.

## Preserving function metadata

`functools.wraps` is commonly used when creating decorators. It preserves information such as the original function's name and docstring.

```python
from functools import wraps
```

Without `@wraps`, the decorated function may appear to have the name of the wrapper function instead of its original name.

## Stacking decorators

Multiple decorators can be applied to the same function:

```python
@log_call
@timer
def add(a, b):
    return a + b
```

The order matters because decorators are applied from the bottom upward:

```python
add = log_call(timer(add))
```

## Exercise

Implement the following decorators:

### `@log_call`

Print the function name every time it is called and preserve its metadata.

### `@repeat(n)`

Execute the decorated function `n` times and return the result of the final call.

### `@timer`

Measure how long the function takes using `time.perf_counter()` and print the elapsed time.

Use all three decorators in a small example program and experiment with changing their order.

## Reference

[Real Python — Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)