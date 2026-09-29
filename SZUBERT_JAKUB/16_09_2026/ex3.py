import functools
import time

# Helper function to convert lists, dicts, and sets to tuples (making them hashable)
def make_hashable(val):
    if isinstance(val, (list, tuple)):
        return tuple(make_hashable(x) for x in val)
    if isinstance(val, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in val.items()))
    if isinstance(val, set):
        return tuple(sorted(make_hashable(x) for x in val))
    return val

def memoize(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Convert all positional and keyword arguments to hashable structures
        key_args = make_hashable(args)
        key_kwargs = make_hashable(kwargs)
        key = (key_args, key_kwargs)
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

# 1. Fibonacci with custom @memoize
@memoize
def fib_memo(n):
    if n < 2:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# 2. Fibonacci with functools.lru_cache
@functools.lru_cache(maxsize=128)
def fib_lru(n):
    if n < 2:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)

if __name__ == "__main__":
    print("--- Fibonacci Performance Comparison fib(35) ---")
    
    start = time.perf_counter()
    res1 = fib_memo(35)
    t1 = time.perf_counter() - start
    print(f"Custom @memoize: fib(35) = {res1} (time: {t1:.6f}s)")

    start = time.perf_counter()
    res2 = fib_lru(35)
    t2 = time.perf_counter() - start
    print(f"lru_cache:       fib(35) = {res2} (time: {t2:.6f}s)")

    print("\nCache info for lru_cache:")
    print(fib_lru.cache_info())

    print("\n--- Testing unhashable arguments (e.g. list) ---")
    @memoize
    def process_list(numbers):
        print("Calculating sum...")
        return sum(numbers)

    print("First call:", process_list([1, 2, 3]))
    print("Second call (from cache):", process_list([1, 2, 3]))