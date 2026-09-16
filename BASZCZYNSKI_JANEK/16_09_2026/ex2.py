import functools
import logging
import time
import unittest
from unittest.mock import call, patch
from typing import Tuple, Type

# =====================================================================
# Logger Setup
# =====================================================================
logger = logging.getLogger("retry_decorator")


# =====================================================================
# 1-4. The Enhanced @retry Decorator Implementation
# =====================================================================
def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
):
    """
    Decorator that retries a function with exponential backoff and logging.

    :param times: Total maximum attempts (initial call + retries).
    :param delay: Initial delay between retries in seconds.
    :param backoff_factor: Multiplier applied to delay after each retry.
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
                            f"Function '{func.__name__}' failed on final attempt ({attempt}/{times}): {e}"
                        )
                        raise

                    logger.warning(
                        f"Function '{func.__name__}' failed (attempt {attempt}/{times}): {e}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff_factor

        return wrapper
    return decorator


# =====================================================================
# 1. Demonstration: Function that fails twice, then succeeds
# =====================================================================
def run_demonstration():
    print("\n--- Running Demonstration: Function fails twice, then succeeds ---")
    call_count = 0

    @retry(times=4, delay=0.01, backoff_factor=2.0, exceptions=(ValueError,))
    def unstable_network_call():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError(f"Temporary network error on call #{call_count}")
        return f"Success on attempt #{call_count}"

    result = unstable_network_call()
    print("Demonstration Result:", result)
    print("-" * 65 + "\n")


# =====================================================================
# 5. 6 Unit Tests with Mocked time.sleep (Instant Execution)
# =====================================================================
class TestRetryDecorator(unittest.TestCase):

    @patch("time.sleep")
    def test_1_success_on_first_attempt_does_not_sleep(self, mock_sleep):
        """1. Should return immediately and never call sleep if no error occurs."""
        @retry(times=3, delay=1.0)
        def succeeds():
            return "OK"

        result = succeeds()
        self.assertEqual(result, "OK")
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_2_fails_twice_then_succeeds(self, mock_sleep):
        """2. Should retry twice and succeed on the 3rd attempt."""
        attempts = 0

        @retry(times=3, delay=1.0)
        def fail_twice():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise RuntimeError("Temporary error")
            return "Recovered"

        result = fail_twice()
        self.assertEqual(result, "Recovered")
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_3_exponential_backoff_delays(self, mock_sleep):
        """3. Should increase sleep time exponentially according to backoff_factor."""
        @retry(times=4, delay=1.0, backoff_factor=2.0)
        def always_fails():
            raise RuntimeError("Boom")

        with self.assertRaises(RuntimeError):
            always_fails()

        # Delays: 1.0, then 1.0 * 2.0 = 2.0, then 2.0 * 2.0 = 4.0
        expected_sleep_calls = [call(1.0), call(2.0), call(4.0)]
        self.assertEqual(mock_sleep.call_args_list, expected_sleep_calls)

    @patch("time.sleep")
    def test_4_only_retries_specified_exceptions(self, mock_sleep):
        """4. Should NOT retry unlisted exceptions and raise them immediately."""
        attempts = 0

        @retry(times=3, delay=1.0, exceptions=(ValueError,))
        def raises_type_error():
            nonlocal attempts
            attempts += 1
            raise TypeError("Not a ValueError")

        with self.assertRaises(TypeError):
            raises_type_error()

        # Must fail immediately on attempt 1 without sleeping
        self.assertEqual(attempts, 1)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_5_exceeding_max_retries_raises_original_exception(self, mock_sleep):
        """5. Should raise the final exception after reaching max attempts."""
        attempts = 0

        @retry(times=3, delay=0.5)
        def always_fails():
            nonlocal attempts
            attempts += 1
            raise ValueError(f"Failure #{attempts}")

        with self.assertRaises(ValueError) as ctx:
            always_fails()

        self.assertIn("Failure #3", str(ctx.exception))
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_6_logs_warnings_on_each_retry(self, mock_sleep):
        """6. Should log a warning message for every retry attempt."""
        @retry(times=3, delay=1.0)
        def fail_once():
            if mock_sleep.call_count == 0:
                raise ValueError("First attempt failed")
            return "Done"

        with self.assertLogs("retry_decorator", level="WARNING") as captured_logs:
            result = fail_once()

        self.assertEqual(result, "Done")
        self.assertEqual(len(captured_logs.output), 1)
        self.assertIn("Function 'fail_once' failed (attempt 1/3)", captured_logs.output[0])


# =====================================================================
# Main Execution Entry Point
# =====================================================================
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Run the live demonstration
    run_demonstration()

    # Run the 6 unit tests
    print("--- Running Unit Tests ---")
    unittest.main(argv=["first-arg-is-ignored"], exit=False)

    