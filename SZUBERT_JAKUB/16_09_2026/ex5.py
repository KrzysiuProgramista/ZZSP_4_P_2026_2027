import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"[{func.__name__}] Execution time: {end - start:.6f}s")
        return res
    return wrapper

# --- 1. Class Decorator ---
def time_all_methods(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, timer(attr_value))
    return cls

@time_all_methods
class CalcWithDecorator:
    def add(self, a, b):
        return a + b

    def slow_work(self):
        time.sleep(0.05)

# --- 2. Metaclass ---
class TimerMeta(type):
    def __new__(mcs, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if callable(attr_value) and not attr_name.startswith("__"):
                attrs[attr_name] = timer(attr_value)
        return super().__new__(mcs, name, bases, attrs)

class CalcWithMeta(metaclass=TimerMeta):
    def add(self, a, b):
        return a + b

    def slow_work(self):
        time.sleep(0.05)

"""
READABILITY COMPARISON COMMENT:
The class decorator (@time_all_methods) is MUCH more readable than the metaclass approach.

Reasons:
1. Syntax is simple and explicit — using `@` directly above the class definition is standard Pythonic style.
2. Metaclasses overcomplicate the class creation flow by inheriting from `type`, adding unnecessary abstraction for this task.
3. Metaclasses can lead to metaclass conflicts during multiple inheritance, whereas class decorators wrap the finalized class cleanly.
"""

if __name__ == "__main__":
    print("--- Testing Class Decorator ---")
    c1 = CalcWithDecorator()
    c1.add(2, 3)
    c1.slow_work()

    print("\n--- Testing Metaclass ---")
    c2 = CalcWithMeta()
    c2.add(4, 5)
    c2.slow_work()