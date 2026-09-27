import functools
import time


def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[LOG] Wywołanie: {func.__name__} z args={args}")
        result = func(*args, **kwargs)
        print(f"[LOG] Zakończono: {func.__name__} -> {result}")
        return result

    return wrapper


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[TIMER] Start pomiaru dla {func.__name__}")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[TIMER] Stop pomiaru: {end - start:.6f} s")
        return result

    return wrapper


@logged
@timer
def slow_add_1(a, b):
    time.sleep(0.1)
    return a + b


@timer
@logged
def slow_add_2(a, b):
    time.sleep(0.1)
    return a + b


if __name__ == "__main__":
    print("--- 1. KOLEJNOŚĆ: @logged NA GÓRZE, @timer NA DOLE ---")
    slow_add_1(2, 3)

    print("\n--- 2. KOLEJNOŚĆ: @timer NA GÓRZE, @logged NA DOLE ---")
    slow_add_2(4, 5)