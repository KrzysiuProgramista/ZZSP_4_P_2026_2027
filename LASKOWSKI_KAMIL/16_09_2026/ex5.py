import functools
import time


def timer(func):
    """
    Decorator designed for functions and methods.
    Since `self` or `cls` is passed as `args[0]`, standard *args, **kwargs
    automatically captures instance and class references seamlessly.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        if args and hasattr(args[0], "__class__"):
            cls_name = args[0].__class__.__name__
            print(f"[Timer] {cls_name}.{func.__name__} took {elapsed:.6f}s")
        else:
            print(f"[Timer] {func.__name__} took {elapsed:.6f}s")
            
        return result

    return wrapper



def time_all_methods(cls):
    """
    Class decorator that inspects all class attributes and wraps
    every user-defined callable method with @timer.
    """
    for attr_name, attr_value in list(cls.__dict__.items()):
        if attr_name.startswith("__") and attr_name.endswith("__"):
            continue

        if callable(attr_value):
            setattr(cls, attr_name, timer(attr_value))
        elif isinstance(attr_value, (staticmethod, classmethod)):
            original_func = attr_value.__func__
            wrapped = timer(original_func)
            if isinstance(attr_value, staticmethod):
                setattr(cls, attr_name, staticmethod(wrapped))
            else:
                setattr(cls, attr_name, classmethod(wrapped))

    return cls


class TimerMeta(type):
    """
    Metaclass that decorates every method with @timer during class creation.
    """
    def __new__(mcs, name, bases, namespace):
        for attr_name, attr_value in list(namespace.items()):
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue

            if callable(attr_value):
                namespace[attr_name] = timer(attr_value)
            elif isinstance(attr_value, (staticmethod, classmethod)):
                original_func = attr_value.__func__
                wrapped = timer(original_func)
                if isinstance(attr_value, staticmethod):
                    namespace[attr_name] = staticmethod(wrapped)
                else:
                    namespace[attr_name] = classmethod(wrapped)

        return super().__new__(mcs, name, bases, namespace)

print("--- Testing Class Decorator ---")

@time_all_methods
class ProcessingEngine:
    def compute_squares(self, count: int) -> list[int]:
        return [i * i for i in range(count)]

    def heavy_calculation(self, n: int) -> int:
        return sum(i**2 for i in range(n))


engine = ProcessingEngine()
engine.compute_squares(100_000)
engine.heavy_calculation(500_000)


print("\n--- Testing Metaclass ---")

class DataPipeline(metaclass=TimerMeta):
    def transform(self, items: list[int]) -> list[int]:
        return [x * 2 for x in items]


pipeline = DataPipeline()
pipeline.transform(list(range(200_000)))