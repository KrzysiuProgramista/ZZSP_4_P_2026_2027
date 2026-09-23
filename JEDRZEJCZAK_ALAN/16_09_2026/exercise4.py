import functools
import inspect
import typing
import warnings


# 1. @validate_types

def validate_types(func):
    sig = inspect.signature(func)
    hints = typing.get_type_hints(func)
    hints.pop("return", None)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            expected = hints.get(name)
            if expected is None:
                continue
            # typing.get_type_hints turns `int | str` / Optional[int] into
            # a typing construct; isinstance needs a plain tuple of types
            # for that, which get_args gives us.
            origin = typing.get_origin(expected)
            if origin is typing.Union:
                allowed = typing.get_args(expected)
            else:
                allowed = (expected,)
            if not isinstance(value, allowed):
                type_names = " | ".join(t.__name__ for t in allowed)
                raise TypeError(
                    f"{func.__name__}(): argument '{name}' must be "
                    f"{type_names}, got {type(value).__name__}"
                )
        return func(*args, **kwargs)
    return wrapper


# 2. @require_positive("amount")
def require_positive(*param_names):
    """Validate that the named argument(s) are > 0."""

    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for name in param_names:
                if name not in bound.arguments:
                    raise ValueError(f"require_positive: no such parameter '{name}'")
                value = bound.arguments[name]
                if value <= 0:
                    raise ValueError(
                        f"{func.__name__}(): '{name}' must be positive, got {value}"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 3. @deprecated("use new_function instead")
def deprecated(message=""):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated. {message}".strip(),
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Demo
if __name__ == "__main__":
    @validate_types
    def greet(name: str, times: int = 1) -> str:
        return (name + " ") * times

    print(greet("Ada", 2))
    try:
        greet("Ada", "twice")
    except TypeError as e:
        print("validate_types caught:", e)

    @require_positive("amount")
    def withdraw(amount):
        return f"withdrew {amount}"

    print(withdraw(50))
    try:
        withdraw(-10)
    except ValueError as e:
        print("require_positive caught:", e)

    def new_function():
        return "new behavior"

    @deprecated("use new_function instead")
    def old_function():
        return new_function()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        old_function()
        print("deprecated warning:", caught[0].message)
