import functools
import time

def _make_hashable(item):
    """Recursively converts unhashable objects into hashable representations."""
    if isinstance(item, (list, tuple)):
        return tuple(_make_hashable(x) for x in item)
    if isinstance(item, (set, frozenset)):
        return frozenset(_make_hashable(x) for x in item)
    if isinstance(item, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in item.items()))
    return item

def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hashable_args = _make_hashable(args)
        hashable_kwargs = _make_hashable(kwargs)
        key = (hashable_args, hashable_kwargs)

        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    return wrapper

def fib_naive(n):
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)

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

print("Benchmarking fib(35)...")

start = time.perf_counter()
res_memo = fib_memoized(35)
time_memo = time.perf_counter() - start
print(f"Custom @memoize: {res_memo} in {time_memo:.6f} seconds")

start = time.perf_counter()
res_lru = fib_lru(35)
time_lru = time.perf_counter() - start
print(f"functools.lru_cache: {res_lru} in {time_lru:.6f} seconds")

print("lru_cache info:", fib_lru.cache_info())