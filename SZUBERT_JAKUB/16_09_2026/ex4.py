import functools
import inspect
import typing
import warnings

# --- @validate_types ---
def validate_types(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        
        hints = typing.get_type_hints(func)
        
        for name, value in bound.arguments.items():
            if name in hints:
                expected_type = hints[name]
                if not isinstance(value, expected_type):
                    raise TypeError(f"Argument '{name}' must be of type {expected_type.__name__}, got {type(value).__name__}")
        return func(*args, **kwargs)
    return wrapper

# --- @require_positive ---
def require_positive(arg_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            if arg_name in bound.arguments:
                val = bound.arguments[arg_name]
                if val <= 0:
                    raise ValueError(f"Argument '{arg_name}' must be positive (> 0), got {val}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

# --- @deprecated ---
def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(f"{func.__name__} is deprecated: {reason}", category=DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage examples
@validate_types
def repeat(text: str, times: int) -> str:
    return text * times

@require_positive("amount")
def pay(amount):
    return f"Paid {amount} USD"

@deprecated("use new_pay() instead")
def old_pay():
    return "Old payment process"

if __name__ == "__main__":
    print("--- @validate_types ---")
    print(repeat("Hello ", 3))
    try:
        repeat("Hello ", "3")
    except TypeError as e:
        print("Caught expected error:", e)

    print("\n--- @require_positive ---")
    print(pay(50))
    try:
        pay(-10)
    except ValueError as e:
        print("Caught expected error:", e)

    print("\n--- @deprecated ---")
    old_pay()