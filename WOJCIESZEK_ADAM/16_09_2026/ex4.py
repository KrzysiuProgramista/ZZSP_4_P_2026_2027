import functools
import inspect
import warnings
from typing import get_type_hints

def validate_types(func):
    hints = get_type_hints(func)
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for param_name, value in bound.arguments.items():
            if param_name in hints:
                expected_type = hints[param_name]
                if not isinstance(value, expected_type):
                    raise TypeError(
                        f"Argument {param_name!r} must be {expected_type.__name__}, got {type(value).__name__}"
                    )
        result = func(*args, **kwargs)
        if "return" in hints:
            expected_return = hints["return"]
            if not isinstance(result, expected_return):
                raise TypeError(
                    f"Return value must be {expected_return.__name__}, got {type(result).__name__}"
                )
        return result
    return wrapper

def require_positive(param_name):
    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            if param_name in bound.arguments:
                val = bound.arguments[param_name]
                if val <= 0:
                    raise ValueError(f"Parameter {param_name!r} must be positive (> 0). Got {val}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__!r} is deprecated: {reason}",
                category=DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@deprecated("Use calculate_total instead")
@require_positive("amount")
@validate_types
def process_payment(account: str, amount: float) -> bool:
    return True

# process_payment("ACC123", -50.0)  # Raises ValueError: Parameter 'amount' must be positive
# process_payment("ACC123", "fifty") # Raises TypeError: Argument 'amount' must be float