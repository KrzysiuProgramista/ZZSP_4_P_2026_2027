import functools

def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("-> Entering [logged]")
        res = func(*args, **kwargs)
        print("<- Exiting [logged]")
        return res
    return wrapper

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("-> Entering [timer]")
        res = func(*args, **kwargs)
        print("<- Exiting [timer]")
        return res
    return wrapper

print("--- Order 1: @logged then @timer ---")
@logged
@timer
def slow_add_1(a, b):
    print("   [slow_add_1 body]")
    return a + b

slow_add_1(2, 3)

print("\n--- Order 2: Swapped (@timer then @logged) ---")
@timer
@logged
def slow_add_2(a, b):
    print("   [slow_add_2 body]")
    return a + b

slow_add_2(2, 3)