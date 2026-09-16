# Python decorators

**Author:** Hubert Zarychta  
**Date:** 16 September 2026

## Exercise 0: Notes

These notes summarise [Primer on Python Decorators — Real Python](https://realpython.com/primer-on-python-decorators/) in my own words.

A function decorator accepts a function and returns a callable, usually a wrapper. The wrapper can add behaviour before or after calling the original function, without editing its body.

Python functions are objects. We can pass them as arguments, return them from other functions, and define functions inside functions. A wrapper can remember the original function through a closure.

The syntax:

```python
@logged
def add(a, b):
    return a + b
```

is equivalent to defining `add` normally and then writing:

```python
add = logged(add)
```

The decorator runs when the function is defined. The returned wrapper runs whenever the decorated function is called.

In a reusable wrapper, `*args` collects positional arguments and `**kwargs` collects keyword arguments. Passing both to the original function preserves its inputs. Returning its result preserves its output.

Decorators can handle logging, timing, counting calls, caching, or checking access. They help reuse the same behaviour across several functions.

## Why use functools.wraps?

Use `@functools.wraps(func)` above the wrapper. It copies metadata such as `__name__` and `__doc__` and sets `__wrapped__` to the original function. See the [Python functools documentation](https://docs.python.org/3/library/functools.html#functools.wraps).

By default, `inspect.signature()` follows `__wrapped__`, so it can show the original parameters. `wraps` does not change the wrapper's actual `*args, **kwargs` parameters. See the [Python inspect documentation](https://docs.python.org/3/library/inspect.html#inspect.signature).

For the `add` function in this solution:

| Inspected value | With wraps | Without wraps |
| --- | --- | --- |
| `add.__name__` | `add` | `wrapper` |
| `add.__doc__` | `Return a plus b.` | `None` |
| `inspect.signature(add)` | `(a, b)` | `(*args, **kwargs)` |

The version without `wraps` exists only to demonstrate the difference.

## Exercise 1: Implementation

All code is in `exercise_1.py`:

- `logged` prints the function name and returned value; it decorates `add`, `multiply`, and `greet`.
- `timer` prints elapsed seconds, including when the function raises an exception.
- `count_calls` exposes a separate `.calls` counter for each decorated function. It starts at zero and counts every call, including failed calls.
- The demonstration prints `add.__name__`, `add.__doc__`, and its inspected signature with and without `wraps`.

Timing uses differences between two `time.perf_counter()` readings, as described in the [Python time documentation](https://docs.python.org/3/library/time.html#time.perf_counter).

The supplied starter code needs `wrapper(*args, **kwargs)`, `func(*args, **kwargs)`, and `func.__name__`.

## Run

From the repository root on Windows:

```powershell
py Zarychta_Hubert/16_09_2026/exercise_1.py
```

On Linux or macOS:

```bash
python3 Zarychta_Hubert/16_09_2026/exercise_1.py
```

Only the Python standard library is used. No additional packages are needed. Timing values vary between runs.
