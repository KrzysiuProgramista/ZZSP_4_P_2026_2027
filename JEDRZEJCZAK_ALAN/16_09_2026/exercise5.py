
import functools
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        # args[0] is `self` here, so we can still report which instance ran.
        owner = args[0].__class__.__name__ if args else ""
        print(f"{owner}.{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper


# 2. Class decorator: wrap every method of a class with @timer.

def time_all_methods(cls):
    for name, value in vars(cls).items():
        # Only wrap plain instance methods, not dunders/staticmethods/etc.
        if callable(value) and not name.startswith("__"):
            setattr(cls, name, timer(value))
    return cls


@time_all_methods
class Calculator:
    def add(self, a, b):
        time.sleep(0.01)
        return a + b

    def multiply(self, a, b):
        time.sleep(0.01)
        return a * b


@timer
class NaivelyTimedCalculator:
    def __init__(self, label="calc"):
        self.label = label

    def add(self, a, b):
        time.sleep(0.01)
        return a + b


class TimingMeta(type):
    def __new__(mcs, name, bases, namespace):
        for attr_name, value in namespace.items():
            if callable(value) and not attr_name.startswith("__"):
                namespace[attr_name] = timer(value)
        return super().__new__(mcs, name, bases, namespace)


class CalculatorMeta(metaclass=TimingMeta):
    def add(self, a, b):
        time.sleep(0.01)
        return a + b

    def multiply(self, a, b):
        time.sleep(0.01)
        return a * b



if __name__ == "__main__":
    print("-- @timer applied to the class itself (the pitfall) --")
    naive = NaivelyTimedCalculator()   # this line IS timed (instantiation)
    naive.add(2, 3)                    # this line is NOT timed -- no output

    print("\n-- class decorator version (@time_all_methods) --")
    calc = Calculator()
    calc.add(2, 3)
    calc.multiply(4, 5)

    print("\n-- metaclass version --")
    calc2 = CalculatorMeta()
    calc2.add(2, 3)
    calc2.multiply(4, 5)
