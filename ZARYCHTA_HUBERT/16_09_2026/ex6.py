"""Exercise 6: stacking decorators and observing execution order."""

import functools
import time

from ex5 import timer


def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"logged: enter {func.__qualname__}")
        try:
            return func(*args, **kwargs)
        finally:
            print(f"logged: exit {func.__qualname__}")

    return wrapper


@logged
@timer
def slow_add(a, b):
    print("body: slow_add")
    time.sleep(0.01)
    return a + b


@timer
@logged
def slow_add_swapped(a, b):
    print("body: slow_add_swapped")
    time.sleep(0.01)
    return a + b


def run_demo():
    print("\nExercise 6: decorator stacking")
    # Decoration is bottom-up: slow_add = logged(timer(original_slow_add)).
    # Calls enter the outer wrapper first and unwind in the opposite order.
    print("Prediction: logged enter -> timer enter -> body -> timer exit -> logged exit")
    print("Result:", slow_add(2, 3))
    print("\nPrediction: timer enter -> logged enter -> body -> logged exit -> timer exit")
    print("Result:", slow_add_swapped(2, 3))
    print("With timer outside logged, elapsed time includes both logging messages.")

if __name__ == "__main__":
    run_demo()
