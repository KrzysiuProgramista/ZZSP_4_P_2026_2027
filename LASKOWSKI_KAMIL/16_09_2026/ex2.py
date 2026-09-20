import functools
import logging
import time

logger = logging.getLogger("retry_decorator")


def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[BaseException], ...] | type[BaseException] = (Exception,),
):
    """
    Decorator that retries a function upon failure.

    :param times: Total number of attempts allowed.
    :param delay: Initial delay between retries in seconds.
    :param backoff: Multiplier applied to delay after each failed attempt.
    :param exceptions: Exception class or tuple of exception classes to catch and retry.
    """
    if not isinstance(exceptions, tuple):
        exceptions = (exceptions,)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        logger.warning(
                            f"Attempt {attempt}/{times} failed for '{func.__name__}': {e}. "
                            "Exhausted all retries."
                        )
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt}/{times} failed for '{func.__name__}' with error: {e}. "
                        f"Retrying in {current_delay}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator