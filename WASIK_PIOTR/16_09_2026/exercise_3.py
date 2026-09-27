import functools
import time


def memoize(func):
    cache = {}

    def _make_hashable(arg):
        if isinstance(arg, dict):
            return tuple(sorted((k, _make_hashable(v)) for k, v in arg.items()))
        if isinstance(arg, list):
            return tuple(_make_hashable(v) for v in arg)
        if isinstance(arg, set):
            return tuple(sorted(_make_hashable(v) for v in arg))
        return arg

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        hashable_args = tuple(_make_hashable(arg) for arg in args)
        hashable_kwargs = tuple(
            sorted((k, _make_hashable(v)) for k, v in kwargs.items())
        )
        key = (hashable_args, hashable_kwargs)

        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

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


@memoize
def process_data(data):
    return f"Przetworzono {len(data)} elementów"


if __name__ == "__main__":
    print("--- 1. TEST UNHASHABLE ARGUMENTS ---")
    list_arg = [1, 2, {"a": [3, 4]}]
    print(process_data(list_arg))
    print(process_data(list_arg))

    print("\n--- 2. PORÓWNANIE WYDAJNOŚCI FOR FIB(35) ---")

    start = time.perf_counter()
    res_memo = fib_memoized(35)
    end = time.perf_counter()
    time_memo = end - start
    print(f"fib_memoized(35) = {res_memo} (czas: {time_memo:.6f} s)")

    start = time.perf_counter()
    res_lru = fib_lru(35)
    end = time.perf_counter()
    time_lru = end - start
    print(f"fib_lru(35)      = {res_lru} (czas: {time_lru:.6f} s)")

    print("\nLiczenie fib_naive(35) bez cache...")
    start = time.perf_counter()
    res_naive = fib_naive(35)
    end = time.perf_counter()
    time_naive = end - start
    print(f"fib_naive(35)    = {res_naive} (czas: {time_naive:.6f} s)")

    print(
        f"\nMemoizacja jest ok. {time_naive / time_memo:.0f} razy szybsza od wersji bez cache!"
    )

    print("\n--- 3. CACHE INFO DLA LRU_CACHE ---")
    print("fib_lru.cache_info():", fib_lru.cache_info())