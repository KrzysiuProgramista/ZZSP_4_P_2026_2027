"""Exercise 5: methods, class decorators, and metaclasses."""

import functools
import inspect
import time


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"timer: enter {func.__qualname__}")
        started = time.perf_counter()
        try:
            # For an instance method, args[0] is self; forward it unchanged.
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - started
            print(f"timer: exit {func.__qualname__} ({elapsed:.6f}s)")

    return wrapper


def _timed_attribute(attribute):
    # Preserve descriptors so class/instance binding still works correctly.
    if isinstance(attribute, staticmethod):
        return staticmethod(timer(attribute.__func__))
    if isinstance(attribute, classmethod):
        return classmethod(timer(attribute.__func__))
    if inspect.isfunction(attribute):
        return timer(attribute)
    return attribute


def time_all_methods(cls):
    """Time methods defined by this class, including __init__ and descriptors.

    Inherited methods and property accessors are not changed. This example is
    for synchronous Python methods; async methods need an async wrapper.
    """
    for name, attribute in list(vars(cls).items()):
        replacement = _timed_attribute(attribute)
        if replacement is not attribute:
            setattr(cls, name, replacement)
    return cls


class TimedMeta(type):
    def __new__(metacls, name, bases, namespace, **kwargs):
        timed_namespace = {
            key: _timed_attribute(value) for key, value in namespace.items()
        }
        return super().__new__(metacls, name, bases, timed_namespace, **kwargs)


class Calculator:
    @timer
    def add(self, a, b):
        return a + b


@time_all_methods
class DecoratedCalculator:
    def __init__(self, bias=0):
        self.bias = bias

    def add(self, a, b):
        return self.bias + a + b

    @staticmethod
    def multiply(a, b):
        return a * b

    @classmethod
    def name(cls):
        return cls.__name__


class MetaCalculator(metaclass=TimedMeta):
    def add(self, a, b):
        return a + b


# The class decorator is more readable here: it explicitly shows the timing
# behavior beside the class and needs no knowledge of metaclass construction.
# The metaclass also wraps methods newly defined by subclasses that inherit it;
# the class decorator must be applied again to wrap new subclass methods.


def run_demo():
    print("\nExercise 5: method and class decorators")
    print("One decorated method:", Calculator().add(2, 3))
    calculator = DecoratedCalculator(bias=10)
    print("Class-decorated method:", calculator.add(2, 3))
    print("Static method:", calculator.multiply(2, 3))
    print("Class method:", calculator.name())
    print("Metaclass:", MetaCalculator().add(2, 3))

if __name__ == "__main__":
    run_demo()
