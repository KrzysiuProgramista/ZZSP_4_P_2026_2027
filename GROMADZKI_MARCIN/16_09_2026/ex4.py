import functools
import inspect
import typing
import warnings

# ==========================================
# Exercise 4: Validation decorators
# ==========================================

# 1. Type Validator
def validate_types(func):
    """Checks arguments against the function's type hints and raises TypeError on a mismatch."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Pobranie sygnatury i przypisanie argumentów
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()
        
        # Pobranie type hints
        hints = typing.get_type_hints(func)
        
        for name, value in bound_args.arguments.items():
            if name in hints:
                expected_type = hints[name]
                # Walidacja za pomocą isinstance
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Argument '{name}' must be of type {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
        return func(*args, **kwargs)
    return wrapper

# 2. Positive Value Validator
def require_positive(arg_name):
    """Validates that a named argument is strictly positive."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            if arg_name in bound_args.arguments:
                val = bound_args.arguments[arg_name]
                if val <= 0:
                    raise ValueError(f"Argument '{arg_name}' must be positive. Got: {val}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 3. Deprecated Warning
def deprecated(message):
    """Emits a warning when the decorated function is called."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Function {func.__name__} is deprecated: {message}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ==========================================
# Testing Exercise 4
# ==========================================
if __name__ == "__main__":
    print("--- Testing @validate_types ---")
    @validate_types
    def add_numbers(a: int, b: int) -> int:
        return a + b

    print(f"Valid addition: {add_numbers(5, 10)}")
    try:
        add_numbers(5, "10") # Should raise TypeError
    except TypeError as e:
        print(f"Caught Type Error successfully: {e}")

    print("\n--- Testing @require_positive ---")
    @require_positive("amount")
    def withdraw(amount, balance=1000):
        return balance - amount

    print(f"Valid withdrawal: {withdraw(100)}")
    try:
        withdraw(-50) # Should raise ValueError
    except ValueError as e:
        print(f"Caught Value Error successfully: {e}")

    print("\n--- Testing @deprecated ---")
    @deprecated("use new_function instead")
    def old_function():
        return "I am old."

    # This will print a warning to stderr
    old_function()