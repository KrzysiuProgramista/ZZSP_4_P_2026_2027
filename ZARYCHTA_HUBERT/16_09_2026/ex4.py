"""Exercise 4: validate arguments, require positivity, and emit warnings.

validate_types supports ordinary runtime classes, Any, unions (including
Optional), Annotated, Literal, and nested list/dict/tuple/set/frozenset hints.
Other typing constructs raise TypeError instead of silently skipping validation.
Like isinstance(), an int annotation accepts bool; float does not accept int.
Return annotations are deliberately not checked: this exercise checks arguments.
"""

from __future__ import annotations

import functools
import inspect
import types
import typing
import warnings


def _matches_type(value, hint):
    """Recursively check the supported hints, including container contents."""
    if hint is typing.Any:
        return True
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin in (typing.Union, types.UnionType):
        return any(_matches_type(value, option) for option in args)
    if origin is typing.Annotated:
        return _matches_type(value, args[0])
    if origin is typing.Literal:
        return any(type(value) is type(option) and value == option for option in args)
    if origin in (list, set, frozenset):
        return isinstance(value, origin) and (
            not args or all(_matches_type(item, args[0]) for item in value)
        )
    if origin is dict:
        return isinstance(value, dict) and (
            not args or all(
                _matches_type(key, args[0]) and _matches_type(item, args[1])
                for key, item in value.items()
            )
        )
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(_matches_type(item, args[0]) for item in value)
        if hint is typing.Tuple:
            return True
        return len(value) == len(args) and all(
            _matches_type(item, item_hint) for item, item_hint in zip(value, args)
        )
    if origin is None and isinstance(hint, type):
        return isinstance(value, hint)
    raise TypeError(f"Unsupported runtime type hint: {hint!r}")


def validate_types(func):
    signature = inspect.signature(func)
    hints = typing.get_type_hints(func, include_extras=True)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # bind handles positional/keyword arguments and rejects invalid calls.
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            if name not in hints:
                continue
            hint = hints[name]
            kind = signature.parameters[name].kind
            if kind is inspect.Parameter.VAR_POSITIONAL:
                values = [(f"{name}[{index}]", item) for index, item in enumerate(value)]
            elif kind is inspect.Parameter.VAR_KEYWORD:
                values = [(f"{name}[{key!r}]", item) for key, item in value.items()]
            else:
                values = [(name, value)]
            for label, item in values:
                if not _matches_type(item, hint):
                    raise TypeError(
                        f"{func.__name__}(): {label} must match {hint!r}; "
                        f"got {type(item).__name__}"
                    )
        return func(*args, **kwargs)

    return wrapper


def require_positive(argument_name):
    def decorator(func):
        signature = inspect.signature(func)
        if argument_name not in signature.parameters:
            raise ValueError(f"{func.__name__} has no parameter {argument_name!r}")
        parameter = signature.parameters[argument_name]
        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD
        ):
            raise ValueError("require_positive needs a single named parameter")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            value = bound.arguments[argument_name]
            if isinstance(value, bool):
                raise TypeError(f"{argument_name} must be a number, not bool")
            try:
                is_positive = value > 0
            except TypeError as exc:
                raise TypeError(f"{argument_name} must be a number") from exc
            if not is_positive:
                raise ValueError(f"{argument_name} must be greater than zero")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def deprecated(message):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is deprecated: {message}",
                category=DeprecationWarning,
                stacklevel=2,  # Point at the caller rather than this wrapper.
            )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@validate_types
def greet(name: str, repeat: int = 1) -> str:
    return " ".join([f"Hello, {name}!"] * repeat)


@validate_types
def total(values: list[int]) -> int:
    return sum(values)


@require_positive("amount")
def deposit(owner, amount=10):
    return f"Deposited {amount} for {owner}"


@deprecated("use new_function instead")
def old_function():
    return "old result"


def run_demo():
    print("\nExercise 4: validation")
    print(greet("Ada", repeat=2))
    print("Nested container validation:", total([1, 2, 3]))
    for bad_call in (lambda: greet("Ada", "twice"), lambda: total([1, "2"])):
        try:
            bad_call()
        except TypeError as exc:
            print("Expected TypeError:", exc)
    print(deposit("Ada", 25))
    print(deposit("Ada", amount=5))
    print(deposit("Ada"))  # The default is also validated.
    try:
        deposit("Ada", amount=0)
    except ValueError as exc:
        print("Expected ValueError:", exc)
    # DeprecationWarning is usually hidden; expose it explicitly in this demo.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        print(old_function())
        print("Captured warning:", caught[0].message)


if __name__ == "__main__":
    run_demo()
