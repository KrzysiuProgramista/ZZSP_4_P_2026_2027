# Python Decorators — Study Notes

Source: [Primer on Python Decorators — Real Python](https://realpython.com/primer-on-python-decorators/)

## Core idea

A decorator is just a regular function that accepts another function as input and hands back a modified version of it. This works because Python functions are first-class objects — they can be passed around, stored in variables, and returned from other functions, exactly like strings or lists.

Writing `@my_decorator` above a function definition is shorthand for `my_func = my_decorator(my_func)`. Nothing magical happens beyond ordinary function calls and reassignment.

## The building blocks

- **First-class functions**: a function name without parentheses is just a reference to that function; adding parentheses calls it.
- **Inner functions**: functions can be defined inside other functions, and they're only visible inside that enclosing scope.
- **Returning functions**: a function can return one of its own inner functions instead of a value, which is what makes decorators possible.

## Minimal decorator pattern

```python
import functools

def my_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # do something before
        result = func(*args, **kwargs)
        # do something after
        return result
    return wrapper
```

Key details worth remembering:
- `*args, **kwargs` in the wrapper let the decorator work on *any* function signature, not just ones with no arguments.
- The wrapper must explicitly `return` the wrapped function's result, or the caller always gets `None` back.
- `@functools.wraps(func)` copies over `__name__`, `__doc__`, and other metadata from the original function onto the wrapper. Skip it and `help()`, debuggers, and frameworks that inspect function signatures (like FastAPI) all get confused, since they'd see the wrapper's identity instead of the real function's.

## Practical decorator examples covered

- **`@timer`** — records `time.perf_counter()` before and after the call and prints the elapsed time.
- **`@debug`** — prints the function's arguments (built from `repr()` of each positional and keyword arg) and its return value on every call. Useful for functions you don't call directly yourself, like patching `math.factorial`.
- **`@slow_down`** — sleeps before calling the function, useful for rate-limiting things like polling a web page.
- **`@register`** — a decorator that *doesn't* wrap the function at all; it just records a reference to it in a global dict and returns it unchanged. This is the basis of a simple plugin system.
- **`login_required`** (Flask-style) — checks an authentication condition before letting the real view function run.

## Decorators on classes

There are two distinct uses:
1. **Decorating individual methods** inside a class (`@property`, `@classmethod`, `@staticmethod` are all built-in examples of this).
2. **Decorating the whole class**, e.g. `@dataclass`. This only wraps the class itself — decorating a class with `@timer` times how long it takes to *instantiate* the class, not its methods, since the class's `__init__`/methods aren't touched.

## Stacking decorators

Multiple decorators can be stacked on one function. They apply bottom-up: the one closest to the function runs first, and each decorator wraps everything below it. Swapping the order of `@debug` and `@do_twice` changes whether the debug output appears once or twice, since it depends on which decorator is "outermost."

## Decorators that take arguments

To let a decorator accept its own arguments (e.g. `@repeat(num_times=4)`), you need an extra layer of nesting: an outer function that takes the decorator's arguments and returns the actual decorator function, which in turn returns the wrapper. This ends up as three nested `def`s and three `return` statements.

A further refinement lets a decorator work both with and without parentheses (`@repeat` and `@repeat(num_times=3)` both valid) by giving the outer function an optional `_func=None` parameter and branching on whether it's `None`.

## Stateful decorators

Decorators can track state across calls:
- **Function-attribute approach**: attach a counter as an attribute on the wrapper function itself (e.g. `wrapper.num_calls`), initialized once when the decorator is applied.
- **Class-based approach**: implement the decorator as a class with `__init__` (storing the function) and `__call__` (running the logic each time the "function" is invoked). `functools.update_wrapper()` is used here instead of `@functools.wraps`, since there's no separate wrapper function to decorate.

## Other real-world patterns mentioned

- **`@singleton`** — makes sure a class only ever has one instance by caching it as an attribute on the wrapper.
- **Caching / memoization** — a hand-rolled `@cache` decorator stores prior results keyed by their arguments; the standard library's `functools.lru_cache` and `functools.cache` do this properly and should be preferred over writing your own.
- **`@set_unit` / `@use_unit`** — attach metadata (like physical units) to a function's return value without changing its core logic.
- **`@validate_json`** — validates incoming JSON payload keys before letting a Flask route handler run, keeping validation logic out of the business logic.

## Takeaways

- A decorator is fundamentally `new_func = decorator(original_func)`.
- Always forward `*args, **kwargs` and return the inner function's result.
- Always apply `@functools.wraps(func)` unless you have a specific reason not to (e.g. `@register`, which intentionally returns the original function unmodified).
- Reach for arguments-to-decorators or class-based decorators only when you actually need configurability or state — the plain wrapper pattern covers most cases.
