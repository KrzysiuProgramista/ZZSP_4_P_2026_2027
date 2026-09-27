import functools
import inspect
import typing
import warnings


def validate_types(func):
    type_hints = typing.get_type_hints(func)
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for arg_name, arg_value in bound_args.arguments.items():
            if arg_name in type_hints:
                expected_type = type_hints[arg_name]
                if not isinstance(arg_value, expected_type):
                    raise TypeError(
                        f"Argument '{arg_name}' musi być typu {expected_type.__name__}, "
                        f"otrzymano {type(arg_value).__name__} ({arg_value!r})."
                    )

        result = func(*args, **kwargs)

        if "return" in type_hints:
            expected_return_type = type_hints["return"]
            if not isinstance(result, expected_return_type):
                raise TypeError(
                    f"Zwracana wartość musi być typu {expected_return_type.__name__}, "
                    f"otrzymano {type(result).__name__} ({result!r})."
                )

        return result

    return wrapper


def require_positive(param_name):
    def decorator(func):
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            if param_name in bound_args.arguments:
                val = bound_args.arguments[param_name]
                if not isinstance(val, (int, float)) or val <= 0:
                    raise ValueError(
                        f"Argument '{param_name}' musi być liczbą dodatnią (> 0), otrzymano: {val!r}"
                    )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def deprecated(reason):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__}() jest przestarzała. {reason}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@validate_types
def add_numbers(a: int, b: int) -> int:
    return a + b


@require_positive("amount")
def withdraw(amount: float, account_id: str):
    return f"Wypłacono {amount} PLN z konta {account_id}"


@deprecated("Użyj nowa_funkcja() zamiast tego.")
def stara_funkcja():
    return "Stara logika"


if __name__ == "__main__":
    print("--- 1. TEST @validate_types ---")
    print("Poprawne wywołanie:", add_numbers(5, 10))

    try:
        add_numbers(5, "10")
    except TypeError as e:
        print("Błąd przechwycony poprawnie:", e)

    print("\n--- 2. TEST @require_positive ---")
    print("Poprawne wywołanie:", withdraw(100.0, "ACC123"))

    try:
        withdraw(-50.0, "ACC123")
    except ValueError as e:
        print("Błąd przechwycony poprawnie:", e)

    print("\n--- 3. TEST @deprecated ---")
    warnings.simplefilter("always", DeprecationWarning)
    print("Wynik funkcji:", stara_funkcja())