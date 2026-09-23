
import functools
import time
import sys



# 1. Basic memoize: dict keyed by arguments

def memoize_naive(func):
    """First pass. Breaks on unhashable args (e.g. a list) because dict
    keys must be hashable — see memoize() below for the fix."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper


# 3. Handle unhashable arguments
def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        raw_key = (args, tuple(sorted(kwargs.items())))
        try:
            hash(raw_key)
            key = raw_key
        except TypeError:
            # Unhashable argument (list, dict, set...) -> fall back to repr.
            key = repr(raw_key)

        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    wrapper.cache_clear = cache.clear
    return wrapper


# 2. Naive recursive fibonacci, with and without memoization
def fib_plain(n):
    if n < 2:
        return n
    return fib_plain(n - 1) + fib_plain(n - 2)


@memoize
def fib_memoized(n):
    if n < 2:
        return n
    return fib_memoized(n - 1) + fib_memoized(n - 2)


@functools.lru_cache(maxsize=128)
def fib_lru(n):
    if n < 2:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)


def timed(label, func, *args):
    start = time.perf_counter()
    result = func(*args)
    elapsed = time.perf_counter() - start
    print(f"{label:<20} result={result:<10} time={elapsed:.6f}s")
    return elapsed


if __name__ == "__main__":
    N = 30  # fib_plain(35) with no memo takes a very long time (~seconds);
            # 30 already makes the point clearly without the wait.
    print(f"Comparing fib({N}):\n")

    sys.setrecursionlimit(10000)

    timed("plain (no cache)", fib_plain, N)
    timed("memoize (custom)", fib_memoized, N)
    timed("lru_cache", fib_lru, N)

    # 3. Unhashable-argument handling demo
    print("\nUnhashable-argument handling:")

    @memoize
    def sum_list(items):
        return sum(items)

    print(sum_list([1, 2, 3]))   # works even though list is unhashable
    print(sum_list([1, 2, 3]))   # served from cache (repr-based key)

    try:
        @memoize_naive
        def sum_list_naive(items):
            return sum(items)
        sum_list_naive([1, 2, 3])
    except TypeError as e:
        print(f"memoize_naive fails as expected: {e}")

    # 5. cache_info()
    print("\nfib_lru.cache_info():", fib_lru.cache_info())
