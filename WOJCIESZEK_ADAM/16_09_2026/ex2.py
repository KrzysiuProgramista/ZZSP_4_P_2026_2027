import functools
import logging
import time

from unittest.mock import patch, call
import pytest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("retry")

def retry(times=3, delay=1.0, backoff=1.0, exceptions=(Exception,)):
    """
    Retries a function if it raises specified exceptions.
    
    :param times: Max number of attempts.
    :param delay: Initial delay between retries in seconds.
    :param backoff: Multiplier for exponential backoff (e.g., 2.0 doubles delay).
    :param exceptions: Tuple of exception types to catch and retry.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        logger.error(
                            f"Attempt {attempt}/{times} for {func.__name__!r} failed with {type(e).__name__}: {e}. No more retries."
                        )
                        raise
                    logger.warning(
                        f"Attempt {attempt}/{times} for {func.__name__!r} failed with {type(e).__name__}: {e}. Retrying in {current_delay:.2f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

@patch("time.sleep", return_value=None)
def test_retry_succeeds_after_failures(mock_sleep):
    calls = 0

    @retry(times=5, delay=0.5)
    def unstable():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("Transient error")
        return "Success"

    assert unstable() == "Success"
    assert calls == 3
    assert mock_sleep.call_count == 2

@patch("time.sleep", return_value=None)
def test_retry_exceeds_max_attempts(mock_sleep):
    @retry(times=3, delay=1.0)
    def always_fails():
        raise RuntimeError("Persistent error")

    with pytest.raises(RuntimeError, match="Persistent error"):
        always_fails()
    assert mock_sleep.call_count == 2

@patch("time.sleep", return_value=None)
def test_exponential_backoff(mock_sleep):
    @retry(times=4, delay=1.0, backoff=2.0)
    def always_fails():
        raise ValueError("Fail")

    with pytest.raises(ValueError):
        always_fails()

    mock_sleep.assert_has_calls([call(1.0), call(2.0), call(4.0)])

@patch("time.sleep", return_value=None)
def test_specific_exception_matching(mock_sleep):
    @retry(times=3, delay=0.5, exceptions=(ValueError,))
    def raises_key_error():
        raise KeyError("Uncaught exception")

    with pytest.raises(KeyError):
        raises_key_error()
    assert mock_sleep.call_count == 0

@patch("time.sleep", return_value=None)
def test_retry_success_on_first_try(mock_sleep):
    @retry(times=3, delay=1.0)
    def instant_success():
        return 42

    assert instant_success() == 42
    assert mock_sleep.call_count == 0

@patch("time.sleep", return_value=None)
def test_retry_passes_arguments_correctly(mock_sleep):
    @retry(times=3, delay=0.1)
    def add(a, b, keyword=0):
        return a + b + keyword

    assert add(2, 3, keyword=5) == 10