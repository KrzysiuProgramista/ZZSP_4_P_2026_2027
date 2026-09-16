import functools
import inspect
import time
from typing import Callable, Type


# =====================================================================
# 1. Method-Safe @timer Decorator
# =====================================================================
def timer(func: Callable) -> Callable:
    """
    Decorator that measures and prints the execution time of a function/method.
    
    Why this works on methods:
    In Python, an instance method is just a regular function where the first
    positional argument is conventional named 'self'. By using *args, 'self'
    is captured naturally as args[0]. We can inspect `args[0].__class__.__name__`
    to dynamically display the owning class name in logs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Infer if this is an instance method call or standalone function
        if args and hasattr(args[0], "__class__") and hasattr(args[0].__class__, func.__name__):
            qualname = f"{args[0].__class__.__name__}.{func.__name__}"
        else:
            qualname = func.__qualname__

        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - start
            print(f"[TIMER] {qualname} took {elapsed:.6f}s")

    return wrapper


# =====================================================================
# Helper: Check if attribute is a regular method to wrap
# =====================================================================
def _is_regular_method(attr_value) -> bool:
    """Returns True if the attribute is a user-defined function (not a dunder/special method)."""
    return (
        inspect.isfunction(attr_value)
        and not (attr_value.__name__.startswith("__") and attr_value.__name__.endswith("__"))
    )


# =====================================================================
# 2. Class Decorator: @time_all_methods
# =====================================================================
def time_all_methods(cls: Type) -> Type:
    """
    Class decorator that inspects the class attributes and wraps all
    callable public methods with @timer.
    """
    # inspect.getmembers(cls, inspect.isfunction) or inspect cls.__dict__
    for attr_name, attr_value in list(cls.__dict__.items()):
        if _is_regular_method(attr_value):
            setattr(cls, attr_name, timer(attr_value))
    return cls


# =====================================================================
# 3. Metaclass Approach: TimerMeta
# =====================================================================
class TimerMeta(type):
    """
    Metaclass that automatically applies @timer to every method defined
    in the class body during class creation.
    """
    def __new__(mcs, name, bases, namespace):
        for attr_name, attr_value in list(namespace.items()):
            if _is_regular_method(attr_value):
                namespace[attr_name] = timer(attr_value)
        return super().__new__(mcs, name, bases, namespace)


# =====================================================================
# 4. Readability & Architectural Comparison
# =====================================================================
"""
===============================================================================
COMPARISON: Class Decorator vs. Metaclass for Method Instrumentation
===============================================================================

WHICH IS MORE READABLE?
--> The CLASS DECORATOR (`@time_all_methods`) is significantly MORE READABLE.

WHY THE CLASS DECORATOR WINS FOR READABILITY:
1. Explicit Intent at the Call Site:
   `@time_all_methods` sits directly above the class header (`class OrderService:`).
   Any developer reading the file immediately understands what is happening
   without having to understand Python's internal class-creation lifecycle.
2. Standard Python Idiom:
   Decorators are beginner-to-intermediate Python concepts used daily (e.g.,
   `@dataclass`, `@classmethod`). Metaclasses are famously an advanced topic
   ("if you don't know whether you need them, you don't").
3. Simpler Debugging:
   Class decorators run AFTER the class object has been fully constructed.
   If something fails, the traceback is linear and easy to inspect.

WHEN WOULD YOU EVER USE THE METACLASS INSTEAD?
The only advantage of `TimerMeta` is INHERITANCE:
- If a base class uses `metaclass=TimerMeta`, ANY SUBCLASS created by any other
  developer will AUTOMATICALLY inherit method timing without needing to remember
  to decorate their class.
- A class decorator only affects the specific class it decorates; subclasses
  do not automatically have their newly declared methods decorated.

VERDICT:
Unless you strictly require mandatory, automatic enforcement down deep inheritance
hierarchies, ALWAYS PREFER CLASS DECORATORS. They are cleaner, less surprising,
and avoid metaclass conflict issues (`TypeError: metaclass conflict`).
===============================================================================
"""


# =====================================================================
# Demonstrations
# =====================================================================

print("=" * 65)
print("1. Testing Single Method Decorated with @timer")
print("=" * 65)

class MathWorker:
    @timer
    def heavy_calculation(self, n: int):
        total = 0
        for i in range(n):
            total += i
        return total

worker = MathWorker()
worker.heavy_calculation(2_000_000)


print("\n" + "=" * 65)
print("2. Testing Class Decorator (@time_all_methods)")
print("=" * 65)

@time_all_methods
class UserService:
    def fetch_user(self, user_id: int):
        time.sleep(0.05)
        return f"User({user_id})"

    def save_preferences(self, user_id: int, theme: str):
        time.sleep(0.02)
        return f"Saved theme={theme} for {user_id}"

service = UserService()
service.fetch_user(101)
service.save_preferences(101, "dark")


print("\n" + "=" * 65)
print("3. Testing Metaclass Approach (TimerMeta)")
print("=" * 65)

class PaymentGateway(metaclass=TimerMeta):
    def authorize(self, amount: float):
        time.sleep(0.03)
        return f"Authorized ${amount}"

    def capture(self, auth_token: str):
        time.sleep(0.04)
        return f"Captured {auth_token}"

gateway = PaymentGateway()
gateway.authorize(99.99)
gateway.capture("tok_12345")