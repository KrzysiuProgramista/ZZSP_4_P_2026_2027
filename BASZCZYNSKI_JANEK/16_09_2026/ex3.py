import functools
import time
from typing import Any


# =====================================================================
# 1 & 3. Custom @memoize handling unhashable arguments
# =====================================================================
def make_hashable(obj: Any) -> Any:
    """
    Recursively converts unhashable objects (lists, dicts, sets)
    into hashable equivalents (tuples, frozensets) so they can be
    used as dictionary keys.
    """
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(x) for x in obj)
    elif isinstance(obj, dict):
        # Sort items by key to make dictionary key-order invariant
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, (set, frozenset)):
        return frozenset(make_hashable(x) for x in obj)
    return obj


def memoize(func):
    """
    Decorator that caches function results in an in-memory dictionary.
    Handles both positional and keyword arguments, as well as unhashable types.
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Convert args and kwargs into hashable representations
        hashable_args = make_hashable(args)
        hashable_kwargs = make_hashable(kwargs)
        cache_key = (hashable_args, hashable_kwargs)

        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)
        return cache[cache_key]

    wrapper.cache = cache  # Expose cache for inspection/clearing if needed
    return wrapper


# =====================================================================
# 2. Fibonacci Implementations
# =====================================================================

# Naive unmemoized: O(2^N) exponential time complexity
def fib_naive(n: int) -> int:
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


# Custom @memoize: O(N) linear time complexity
@memoize
def fib_custom(n: int) -> int:
    if n < 2:
        return n
    return fib_custom(n - 1) + fib_custom(n - 2)


# functools.lru_cache: C-optimized bounded LRU cache
@functools.lru_cache(maxsize=128)
def fib_lru(n: int) -> int:
    if n < 2:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)


# Helper function to demonstrate unhashable arguments
@memoize
def process_user_data(config: dict, tags: list) -> str:
    return f"Config keys: {list(config.keys())}, Total tags: {len(tags)}"


# =====================================================================
# Benchmarks and Comparisons
# =====================================================================
if __name__ == "__main__":
    TARGET = 35

    print("=" * 65)
    print(f"BENCHMARK: Computing fib({TARGET})")
    print("=" * 65)

    # 1. Unmemoized naive fibonacci
    print(f"Running naive fib_naive({TARGET}) ... (this may take 2-4 seconds)")
    start = time.perf_counter()
    res_naive = fib_naive(TARGET)
    time_naive = time.perf_counter() - start
    print(f"-> Naive:          Result = {res_naive} | Time = {time_naive:.6f}s")

    # 2. Custom @memoize
    start = time.perf_counter()
    res_custom = fib_custom(TARGET)
    time_custom = time.perf_counter() - start
    print(f"-> Custom Memoize: Result = {res_custom} | Time = {time_custom:.6f}s")

    # 3. functools.lru_cache(maxsize=128)
    start = time.perf_counter()
    res_lru = fib_lru(TARGET)
    time_lru = time.perf_counter() - start
    print(f"-> lru_cache:      Result = {res_lru} | Time = {time_lru:.6f}s")

    # Speedup calculations
    speedup_custom = time_naive / time_custom if time_custom > 0 else float("inf")
    print("\n" + "-" * 65)
    print(f"Custom @memoize was {speedup_custom:,.1f}x faster than naive!")
    print("-" * 65)

    # =================================================================
    # 4. Cache Info Inspection
    # =================================================================
    print("\n--- lru_cache Cache Info ---")
    print("fib_lru.cache_info():", fib_lru.cache_info())

    # =================================================================
    # 3. Demonstrating Unhashable Argument Handling
    # =================================================================
    print("\n--- Testing Unhashable Arguments Handling ---")
    data_cfg = {"retries": 3, "timeout": 10}
    data_tags = ["prod", "auth", "v2"]

    # Call with mutable list & dict
    first_call = process_user_data(data_cfg, data_tags)
    second_call = process_user_data(data_cfg, data_tags)

    print(f"First call result : {first_call}")
    print(f"Second call result: {second_call}")
    print(f"Cache entries in process_user_data: {len(process_user_data.cache)}")
    print("Unhashable arguments successfully converted and cached without TypeError!")
    print("=" * 65)