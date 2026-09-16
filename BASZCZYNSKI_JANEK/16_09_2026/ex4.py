import functools
import inspect
import typing
import warnings
from typing import get_args, get_origin, get_type_hints


# =====================================================================
# 1. Type Checking Helper & @validate_types Decorator
# =====================================================================
def _check_type(val: typing.Any, expected_type: typing.Any) -> bool:
    """
    Helper function to check if `val` matches `expected_type`,
    supporting basic types (int, str, float), typing.Any, and Unions (including Optional).
    """
    if expected_type is typing.Any:
        return True

    origin = get_origin(expected_type)

    # Handle Union / Optional types (e.g. Union[int, str] or int | None)
    if origin is typing.Union:
        args = get_args(expected_type)
        return any(_check_type(val, arg) for arg in args)

    # If it's a standard class/type (int, str, list, etc.)
    target_type = origin if origin is not None else expected_type
    if isinstance(target_type, type):
        return isinstance(val, target_type)

    return True


def validate_types(func):
    """
    Validates arguments against the function's type annotations.
    Raises TypeError if any passed argument does not match its hinted type.
    """
    sig = inspect.signature(func)
    # get_type_hints resolves stringified annotations (e.g., from __future__ import annotations)
    hints = get_type_hints(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Bind arguments to parameter names, filling in defaults
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, val in bound_args.arguments.items():
            if param_name in hints and param_name != "return":
                expected_type = hints[param_name]
                if not _check_type(val, expected_type):
                    raise TypeError(
                        f"Argument '{param_name}' must be of type {expected_type}, "
                        f"got {type(val).__name__} ({val!r})"
                    )

        return func(*args, **kwargs)

    return wrapper


# =====================================================================
# 2. @require_positive Decorator
# =====================================================================
def require_positive(param_name: str):
    """
    Decorator factory that ensures a named parameter is numeric and > 0.
    Raises ValueError or TypeError if the constraint is violated.
    """
    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            if param_name not in bound_args.arguments:
                raise ValueError(
                    f"Parameter '{param_name}' not found in signature of {func.__name__}"
                )

            val = bound_args.arguments[param_name]

            if not isinstance(val, (int, float)):
                raise TypeError(
                    f"Parameter '{param_name}' must be a number, got {type(val).__name__}"
                )

            if val <= 0:
                raise ValueError(
                    f"Parameter '{param_name}' must be positive (> 0), got {val}"
                )

            return func(*args, **kwargs)

        return wrapper
    return decorator


# =====================================================================
# 3. @deprecated Decorator
# =====================================================================
def deprecated(reason: str = "use new_function instead"):
    """
    Decorator that emits a DeprecationWarning when the decorated function is called.
    stacklevel=2 ensures the warning points to the line where the call was made.
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


# =====================================================================
# Demonstrations & Verification
# =====================================================================
if __name__ == "__main__":
    # Ensure DeprecationWarnings are displayed in the console
    warnings.simplefilter("always", DeprecationWarning)

    print("=" * 65)
    print("1. Testing @validate_types")
    print("=" * 65)

    @validate_types
    def create_user(name: str, age: int, is_admin: bool = False) -> str:
        return f"User({name}, age={age}, admin={is_admin})"

    # Valid call
    print("Valid call:", create_user("Alice", 30))

    # Invalid call 1: age as string
    try:
        create_user("Bob", "thirty")
    except TypeError as err:
        print("Caught expected TypeError:", err)

    # Invalid call 2: is_admin as string via kwargs
    try:
        create_user(name="Charlie", age=25, is_admin="yes")
    except TypeError as err:
        print("Caught expected TypeError:", err)

    print("\n" + "=" * 65)
    print("2. Testing @require_positive")
    print("=" * 65)

    @require_positive("amount")
    def transfer_funds(sender: str, recipient: str, amount: float):
        return f"Transferred ${amount:.2f} from {sender} to {recipient}"

    # Valid call
    print("Valid transfer:", transfer_funds("Alice", "Bob", 150.50))

    # Invalid call: zero or negative
    try:
        transfer_funds("Alice", "Bob", amount=-20.0)
    except ValueError as err:
        print("Caught expected ValueError:", err)

    # Invalid call: non-numeric
    try:
        transfer_funds("Alice", "Bob", amount="100")
    except TypeError as err:
        print("Caught expected TypeError:", err)

    print("\n" + "=" * 65)
    print("3. Testing @deprecated")
    print("=" * 65)

    @deprecated("use `calculate_v2` for faster execution.")
    def calculate_v1(x: int, y: int) -> int:
        return x + y

    print("Calling deprecated function:")
    result = calculate_v1(10, 20)
    print(f"Result: {result}")

    print("\n" + "=" * 65)
    print("4. Combining Decorators")
    print("=" * 65)

    @deprecated("use new billing API")
    @require_positive("rate")
    @validate_types
    def calculate_invoice(hours: int, rate: float) -> float:
        return hours * rate

    total = calculate_invoice(40, 75.0)
    print(f"Combined decorators result: ${total:.2f}")