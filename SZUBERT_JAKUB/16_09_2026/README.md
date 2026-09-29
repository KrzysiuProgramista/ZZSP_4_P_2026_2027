# JAKUB SZUBERT 4TPR

# Primer on Python Decorators

Decorators allow you to modify or extend the behavior of a function or method without permanently altering its actual code.

## 1. What is a Decorator?
In Python, functions are first-class objects. This means functions can be passed around as arguments, returned from other functions, and assigned to variables. A decorator is a function that takes another function as an argument, wraps its behavior in an inner function, and returns the wrapped version.

```python
def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

# @my_decorator is equivalent to: say_hello = my_decorator(say_hello)
```

## 2. Preserving Function Identity
When wrapping a function, the original metadata (like name, docstring, and signature) is lost because it gets replaced by the wrapper function. To preserve the original identity, always use @functools.wraps(func) on the inner wrapper function.

```Python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

## 3. Decorators with Arguments
To pass arguments to a decorator itself, you need an extra layer of nesting (a function that returns a decorator):
```python
def repeat(num_times):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(num_times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator_repeat
```