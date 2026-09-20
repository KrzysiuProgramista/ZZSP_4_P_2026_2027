import functools
import time

def _make_hashable(obj):
    """Recursively converts unhashable objects into hashable representations."""
    if isinstance(obj, (list, tuple)):
        return tuple(_make_hashable(item) for item in obj)
    if isinstance(obj, dict):
        return tuple(sorted((k, _make_hashable(v)) for k, v in obj.items()))
    if isinstance(obj, set):
        return frozenset(_make_hashable(item) for item in obj)
    try:
        hash(obj)
        return obj
    except TypeError:
        return repr(obj)


def memoize(func):
    """Decorator that caches function results by hashable argument signature."""
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (_make_hashable(args), _make_hashable(kwargs))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    wrapper.cache = cache
    return wrapper

def fib_naive(n: int) -> int:
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@memoize
def fib_memoized(n: int) -> int:
    if n < 2:
        return n
    return fib_memoized(n - 1) + fib_memoized(n - 2)


start = time.perf_counter()
res_naive = fib_naive(35)
t_naive = time.perf_counter() - start

start = time.perf_counter()
res_memoized = fib_memoized(35)
t_memoized = time.perf_counter() - start

print(f"fib_naive(35)    = {res_naive} | Time: {t_naive:.4f}s")
print(f"fib_memoized(35) = {res_memoized} | Time: {t_memoized:.6f}s")
print(f"Speedup Factor:  {t_naive / t_memoized:,.0f}x faster")

@memoize
def process_data(items: list, metadata: dict):
    return f"Processed {len(items)} items with key '{metadata.get('env')}'"

print(process_data([1, 2, [3, 4]], {"env": "prod", "tags": {"a", "b"}}))
print(process_data([1, 2, [3, 4]], {"env": "prod", "tags": {"a", "b"}}))