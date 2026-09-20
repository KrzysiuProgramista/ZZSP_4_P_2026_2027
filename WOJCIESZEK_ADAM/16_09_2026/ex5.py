import functools
import inspect
import time

def timer(func):
    """Timer decorator that works for both standalone functions and instance methods."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__qualname__} executed in {elapsed:.6f}s")
        return res
    return wrapper

# --- Class Decorator approach ---
def time_all_methods(cls):
    """Class decorator that applies @timer to every call_able attribute/method."""
    for attr_name, attr_val in cls.__dict__.items():
        if inspect.isfunction(attr_val) and not attr_name.startswith("__"):
            setattr(cls, attr_name, timer(attr_val))
    return cls

@time_all_methods
class CalculatorClassDec:
    def add(self, x, y):
        return x + y

    def multiply(self, x, y):
        return x * y

# --- Metaclass approach ---
class TimeAllMethodsMeta(type):
    """Metaclass that decorates all methods defined on new classes with @timer."""
    def __new__(mcs, name, bases, namespace):
        for attr_name, attr_val in namespace.items():
            if inspect.isfunction(attr_val) and not attr_name.startswith("__"):
                namespace[attr_name] = timer(attr_val)
        return super().__new__(mcs, name, bases, namespace)

class CalculatorMeta(metaclass=TimeAllMethodsMeta):
    def add(self, x, y):
        return x + y

# --- Readability Comparison ---
"""
READABILITY COMPARISON:

1. Class Decorator (@time_all_methods):
   - WINNER for readability.
   - Standard, explicit Python syntax placed directly above the class definition.
   - Clear intent: "Modify this class after creation".

2. Metaclass (metaclass=TimeAllMethodsMeta):
   - Less readable and adds unnecessary complexity for basic method wrapping.
   - Metaclasses affect class creation mechanics and inheritance structures.
   - Use metaclasses only when inheritance propagation is strictly required across subclasses.
"""