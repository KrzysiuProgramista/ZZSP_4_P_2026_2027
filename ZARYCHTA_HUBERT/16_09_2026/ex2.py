"""Exercise 2: a configurable retry decorator, exponential backoff, and logging.

Run this file for a function that fails twice and then succeeds. The demo mocks
sleep so its displayed 0.5- and 1-second delays do not actually slow it down.
"""

import functools
import logging
import math
import time


LOGGER = logging.getLogger(__name__)


def retry(times=3, delay=1, exceptions=(ValueError,), backoff=2):
    """Try up to ``times`` total calls, retrying only the listed exceptions.

    Wait ``delay * backoff ** n`` seconds before retry number ``n + 1``.
    The defaults therefore wait 1, then 2 seconds. Use ``backoff=1`` for
    constant delays. Each actual retry produces a WARNING log entry.
    """
    if isinstance(times, bool) or not isinstance(times, int):
        raise TypeError("times must be an integer")
    if times < 1:
        raise ValueError("times must be at least 1")

    for name, value, minimum in (("delay", delay, 0), ("backoff", backoff, 1)):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not math.isfinite(value) or value < minimum:
            raise ValueError(f"{name} must be finite and at least {minimum}")

    if not isinstance(exceptions, tuple) or not exceptions:
        raise TypeError("exceptions must be a nonempty tuple of Exception classes")
    if any(not isinstance(cls, type) or not issubclass(cls, Exception)
           for cls in exceptions):
        raise TypeError("exceptions must contain only Exception classes")

    # Calling @retry(...) first captures configuration in these enclosing scopes.
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    if attempt == times:
                        # Bare raise preserves the final exception and traceback.
                        raise
                    wait = delay * backoff ** (attempt - 1)
                    LOGGER.warning(
                        "%s failed on attempt %d/%d (%s: %s); retry %d/%d in %g s",
                        func.__name__, attempt, times,
                        type(error).__name__, error, attempt, times - 1, wait,
                    )
                    time.sleep(wait)
        return wrapper
    return decorator


def run_demo():
    """Fail twice, succeed on call three, and display the skipped waits."""
    from unittest.mock import patch

    print("Exercise 2: retries")
    calls = 0

    @retry(times=5, delay=0.5, exceptions=(ValueError,))
    def unstable():
        nonlocal calls
        calls += 1
        if calls <= 2:
            raise ValueError(f"temporary failure {calls}")
        return "success"

    with patch(__name__ + ".time.sleep") as sleep:
        result = unstable()
    print(f"Result: {result}; calls: {calls}")
    print(f"Mocked sleep delays: {[call.args[0] for call in sleep.call_args_list]}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    run_demo()
