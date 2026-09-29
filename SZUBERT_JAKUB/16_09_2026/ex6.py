import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("[LOG] Enter function")
        res = func(*args, **kwargs)
        print("[LOG] Exit function")
        return res
    return wrapper

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("[TIMER] Start timing")
        res = func(*args, **kwargs)
        print("[TIMER] End timing")
        return res
    return wrapper

# Order 1: @logged outer, @timer inner
# Equivalent to: slow_add_1 = logged(timer(slow_add_1))
@logged
@timer
def slow_add_1(a, b):
    print("  -> Executing slow_add_1 body")
    return a + b

# Order 2: Swapped order
# Equivalent to: slow_add_2 = timer(logged(slow_add_2))
@timer
@logged
def slow_add_2(a, b):
    print("  -> Executing slow_add_2 body")
    return a + b

if __name__ == "__main__":
    print("--- Order 1: @logged on top ---")
    slow_add_1(2, 3)

    print("\n--- Order 2: @timer on top ---")
    slow_add_2(2, 3)