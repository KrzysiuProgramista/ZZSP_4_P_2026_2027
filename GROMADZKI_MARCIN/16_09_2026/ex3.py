import functools
import time

# ==========================================
# 1. Custom @memoize Decorator
# ==========================================

def make_hashable(obj):
    """
    Recursively converts unhashable objects (lists, dicts, sets) 
    into hashable ones (tuples, frozensets) so they can be used as dict keys.
    """
    if isinstance(obj, dict):
        # Sort keys to ensure the same dict always produces the same hashable representation
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    elif isinstance(obj, list):
        return tuple(make_hashable(e) for e in obj)
    elif isinstance(obj, set):
        return frozenset(make_hashable(e) for e in obj)
    return obj

def memoize(func):
    """Caches the results of the function in a dictionary."""
    cache = {}
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # We must freeze the arguments into a hashable state
        # Without this, passing a list (e.g., [1, 2]) would throw a TypeError!
        hashable_args = make_hashable(args)
        hashable_kwargs = make_hashable(kwargs)
        cache_key = (hashable_args, hashable_kwargs)
        
        if cache_key not in cache:
            cache[cache_key] = func(*args, **kwargs)
        return cache[cache_key]
    return wrapper


# ==========================================
# 2. Fibonacci Implementations
# ==========================================

# A. Naive (Uncached)
def fib_naive(n):
    if n < 2: return n
    return fib_naive(n - 1) + fib_naive(n - 2)

# B. Custom Memoization
@memoize
def fib_memo(n):
    if n < 2: return n
    return fib_memo(n - 1) + fib_memo(n - 2)

# C. Built-in LRU Cache
@functools.lru_cache(maxsize=128)
def fib_lru(n):
    if n < 2: return n
    return fib_lru(n - 1) + fib_lru(n - 2)


# ==========================================
# 3. Testing and Timing
# ==========================================
if __name__ == "__main__":
    n = 35
    print(f"--- Calculating Fibonacci for n = {n} ---")
    
    # 1. Naive Test
    start = time.perf_counter()
    res_naive = fib_naive(n)
    time_naive = time.perf_counter() - start
    print(f"Naive:   {res_naive} (Took {time_naive:.4f} seconds)")

    # 2. Custom @memoize Test
    start = time.perf_counter()
    res_memo = fib_memo(n)
    time_memo = time.perf_counter() - start
    print(f"Memoize: {res_memo} (Took {time_memo:.6f} seconds)")
    
    # 3. @lru_cache Test
    start = time.perf_counter()
    res_lru = fib_lru(n)
    time_lru = time.perf_counter() - start
    print(f"LRU:     {res_lru} (Took {time_lru:.6f} seconds)")
    print("-" * 50)
    
    # ==========================================
    # 4. Handling Unhashables Test
    # ==========================================
    print("\n--- Testing Unhashable Arguments ---")
    
    @memoize
    def process_data(data):
        # A mock function that processes a list or dict
        return sum(data) if isinstance(data, list) else len(data)
        
    try:
        # A list is inherently unhashable. If our decorator didn't 
        # use `make_hashable`, this would crash with TypeError: unhashable type: 'list'
        process_data([1, 2, 3, 4, 5])
        process_data([1, 2, 3, 4, 5]) # This one hits the cache!
        print("Success! The @memoize decorator handled a mutable list without crashing.")
    except Exception as e:
        print(f"Failed! {e}")
        
    print("-" * 50)

    # ==========================================
    # 5. lru_cache Info
    # ==========================================
    print("\n--- LRU Cache Info ---")
    
    # Run fib_lru a few more times to show cache hits
    fib_lru(35) 
    fib_lru(30)
    
    # .cache_info() is a built-in method provided by functools.lru_cache
    print(fib_lru.cache_info())