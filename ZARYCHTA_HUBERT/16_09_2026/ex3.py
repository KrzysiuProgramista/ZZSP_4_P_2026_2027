"""Exercise 3: dictionary memoization, unhashable inputs, and lru_cache.

Run this file directly to compare three recursive implementations of fib(35).
Use caching for pure functions: returning a previously computed result should
be equivalent to calling the function again.
"""

from functools import lru_cache, wraps
from time import perf_counter


def memoize(func):
    """Cache calls by positional arguments and sorted keyword arguments.

    Calls containing unhashable values (such as lists or dictionaries) execute
    normally without caching. This avoids inventing a potentially ambiguous
    string key or changing the distinction between a list and a tuple.
    Keyword order does not affect the key; positional and keyword spellings
    remain separate keys, even when they mean the same call to the function.
    """
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        try:
            hash(key)
        except TypeError:
            return func(*args, **kwargs)

        # None is a valid cached result; membership is checked explicitly.
        # Exceptions raised by func are not cached.
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


def fib_naive(n):
    """Naive recursion; this example expects an integer n >= 0."""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@memoize
def fib_memoized(n):
    """Recursive calls go through the custom memoized function itself."""
    if n < 2:
        return n
    return fib_memoized(n - 1) + fib_memoized(n - 2)


@lru_cache(maxsize=128)
def fib(n):
    """The standard-library replacement, including caching recursive calls."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


def _timed_call(func, n):
    start = perf_counter()
    result = func(n)
    return result, perf_counter() - start


def run_demo():
    """Print real cold/warm timings and show the unhashable-input policy."""
    print("Exercise 3: caching")
    print("fib(35): first call starts with empty caches; second call reuses them.")
    print("The naive function has no cache on either call.")
    fib_memoized.cache_clear()
    fib.cache_clear()

    for label, function in (
        ("naive", fib_naive),
        ("@memoize", fib_memoized),
        ("@lru_cache(maxsize=128)", fib),
    ):
        first_result, first_seconds = _timed_call(function, 35)
        second_result, second_seconds = _timed_call(function, 35)
        assert first_result == second_result == 9_227_465
        print(
            f"  {label:25} result={first_result:,}  "
            f"first={first_seconds:.6f}s  second={second_seconds:.6f}s"
        )

    print(f"Custom cache entries: {len(fib_memoized.cache)}")
    print(f"fib.cache_info(): {fib.cache_info()}")
    print("Timings vary by machine; tiny cached-call timings include timer noise.")

    calls = 0

    @memoize
    def total(values):
        nonlocal calls
        calls += 1
        return sum(values)

    first = total([1, 2, 3])
    second = total([1, 2, 3])
    print(f"Two calls with lists: results={first}, {second}; body calls={calls}.")
    assert calls == 2

    first = total((1, 2, 3))
    second = total((1, 2, 3))
    print(
        f"Two calls with tuples: results={first}, {second}; "
        f"total body calls={calls} (the second tuple call is cached)."
    )
    assert calls == 3
    print("lru_cache also requires hashable arguments; lists raise TypeError.")


if __name__ == "__main__":
    run_demo()
