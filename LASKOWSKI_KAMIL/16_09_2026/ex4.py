import functools
import inspect
import typing
import warnings

def validate_types(func):
    """
    Checks function arguments against type hints at runtime.
    Raises TypeError on any type mismatch.
    """
    sig = inspect.signature(func)
    type_hints = typing.get_type_hints(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            if name in type_hints:
                expected_type = type_hints[name]
                
                origin = typing.get_origin(expected_type)
                check_type = origin if origin is not None else expected_type

                if check_type is typing.Any:
                    continue

                if not isinstance(value, check_type):
                    raise TypeError(
                        f"Argument '{name}' must be of type {expected_type.__name__ if hasattr(expected_type, '__name__') else expected_type}, "
                        f"got {type(value).__name__} ({value!r})"
                    )

        return func(*args, **kwargs)

    return wrapper

def require_positive(param_name: str):
    """
    Ensures that a named argument passed to the function is > 0.
    Raises ValueError if the argument is missing, non-numeric, or <= 0.
    """
    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            if param_name not in bound.arguments:
                raise ValueError(f"Required positive argument '{param_name}' was not provided.")

            value = bound.arguments[param_name]
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(
                    f"Argument '{param_name}' must be a positive number (> 0), got {value!r}"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator

def deprecated(reason: str):
    """
    Emits a DeprecationWarning when the decorated function is called.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"Call to deprecated function '{func.__name__}': {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator

@validate_types
def process_payment(account_id: int, amount: float, memo: str) -> str:
    return f"Processed ${amount:.2f} for account {account_id}"

print(process_payment(1001, 49.99, "Invoice #1"))

try:
    process_payment("invalid_id", 49.99, "Invoice #1")
except TypeError as e:
    print(f"Caught expected error: {e}")


@require_positive("amount")
def withdraw(account_id: str, amount: float):
    return f"Withdrew ${amount} from {account_id}"

print(withdraw("ACC-42", 150.0))

try:
    withdraw("ACC-42", -50.0)
except ValueError as e:
    print(f"Caught expected error: {e}")


@deprecated("use 'transfer_funds' instead")
@validate_types
@require_positive("amount")
def old_transfer(from_acc: int, to_acc: int, amount: float):
    return f"Transferred ${amount} from {from_acc} to {to_acc}"

with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    res = old_transfer(101, 202, 250.0)
    print(f"\nFunction output: {res}")
    print(f"Warning emitted: {w[0].message}")