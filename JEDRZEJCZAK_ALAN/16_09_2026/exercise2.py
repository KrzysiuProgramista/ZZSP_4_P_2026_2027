import functools
import logging
import time

logger = logging.getLogger("retry")
logging.basicConfig(level=logging.INFO, format="%(message)s")


def retry(_func=None, *, times=3, delay=1, backoff=2, exceptions=(Exception,)):

    def decorator_retry(func):
        @functools.wraps(func)
        def wrapper_retry(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    if attempt == times:
                        logger.warning(
                            "%s: attempt %d/%d failed (%r) - giving up",
                            func.__name__, attempt, times, exc,
                        )
                        raise
                    logger.warning(
                        "%s: attempt %d/%d failed (%r) - retrying in %.2fs",
                        func.__name__, attempt, times, exc, current_delay,
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper_retry

    if _func is None:
        return decorator_retry
    else:
        return decorator_retry(_func)


if __name__ == "__main__":
    # Manual smoke test: fails twice, then succeeds.
    calls = {"n": 0}

    @retry(times=5, delay=0.5)
    def unstable():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError(f"boom on call {calls['n']}")
        return "ok"

    print(unstable(), "after", calls["n"], "calls")

    # Bare-decorator form also works now (uses times=3, delay=1 defaults):
    @retry
    def works_first_try():
        return "instant success"

    print(works_first_try())
