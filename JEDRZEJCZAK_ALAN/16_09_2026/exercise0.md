# Decorators in Python — Notes

## What is a decorator?

A decorator is a function that takes another function (or class) as input,
wraps it with extra behavior, and returns a new callable — usually a
"wrapper" function — that replaces the original.

```python
def logged(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper


@logged
def add(a, b):
    """Return the sum of a and b."""
    return a + b
```

`@logged` above `def add(...)` is exactly equivalent to writing:

```python
def add(a, b):
    """Return the sum of a and b."""
    return a + b

add = logged(add)
```

So after decoration, the name `add` in the module actually points to
`wrapper`, not to the original `add` function.

## The `__name__` / `__docstring__` problem

Because `add` now refers to `wrapper`, introspection breaks:

```python
print(add.__name__)  # "wrapper", not "add"
print(add.__doc__)   # None, not "Return the sum of a and b."
```

This matters for debugging, documentation tools (Sphinx), help(), and
anything that inspects functions by name.

## Fixing it with `functools.wraps`

`functools.wraps` is itself a decorator (a decorator factory, really) that
you apply to the *wrapper* function inside your decorator. It copies over
`__name__`, `__doc__`, `__module__`, `__qualname__`, and `__wrapped__`
(a reference to the original function) from the wrapped function to the
wrapper.

```python
import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```

Now `add.__name__ == "add"` and `add.__doc__` is preserved.

## Other classic decorators

- **`@timer`** — measures and prints wall-clock execution time using
  `time.perf_counter()` before and after the call.
- **`@count_calls`** — keeps a counter (often stored as an attribute on the
  wrapper itself, e.g. `wrapper.calls`) that increments every time the
  function is invoked, so you can inspect `func.calls` later.

## Key takeaways

1. A decorator replaces a function with a wrapper — always use
   `functools.wraps(func)` on your inner wrapper to preserve identity
   and metadata.
2. `*args, **kwargs` in the wrapper signature let the decorator work with
   any function signature.
3. Decorators can carry state (like a call counter) by attaching attributes
   to the wrapper function object, or by using `nonlocal`/closures.
4. Multiple decorators can be stacked; they apply bottom-up.
