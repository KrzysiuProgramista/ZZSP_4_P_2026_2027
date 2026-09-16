import functools
import time
import unittest
from unittest.mock import patch, call

def retry(times=3, delay=1, backoff=2, exceptions=(ValueError,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as err:
                    if attempt == times - 1:
                        raise err
                    print(f"retry attempt {attempt + 1} after failure")
                    time.sleep(current_delay)
                    current_delay = current_delay * backoff
        return wrapper
    return decorator

calls = 0

@retry(times=4, delay=1, backoff=2, exceptions=(ValueError,))
def unstable_worker():
    global calls
    calls = calls + 1
    if calls < 3:
        raise ValueError("broken")
    return "work is done"

print("testing worker that fails twice")
result = unstable_worker()
print(f"result is {result}")

class TestRetryDecorator(unittest.TestCase):

    @patch("time.sleep")
    def test_success_on_first_try(self, mock_sleep):
        @retry(times=3, delay=1)
        def good_function():
            return "good"

        output = good_function()
        self.assertEqual(output, "good")
        self.assertEqual(mock_sleep.call_count, 0)

    @patch("time.sleep")
    def test_fails_twice_then_succeeds(self, mock_sleep):
        attempt_count = 0

        @retry(times=3, delay=1, exceptions=(ValueError,))
        def flaky():
            nonlocal attempt_count
            attempt_count = attempt_count + 1
            if attempt_count < 3:
                raise ValueError("temporary error")
            return "passed"

        output = flaky()
        self.assertEqual(output, "passed")
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_exceeds_max_retries_raises_error(self, mock_sleep):
        @retry(times=3, delay=1, exceptions=(ValueError,))
        def always_fails():
            raise ValueError("always bad")

        with self.assertRaises(ValueError):
            always_fails()

        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_unhandled_exception_not_retried(self, mock_sleep):
        @retry(times=3, delay=1, exceptions=(ValueError,))
        def wrong_error():
            raise TypeError("wrong type error")

        with self.assertRaises(TypeError):
            wrong_error()

        self.assertEqual(mock_sleep.call_count, 0)

    @patch("time.sleep")
    def test_exponential_backoff_delays(self, mock_sleep):
        attempt_count = 0

        @retry(times=3, delay=1, backoff=2, exceptions=(ValueError,))
        def needs_three_tries():
            nonlocal attempt_count
            attempt_count = attempt_count + 1
            if attempt_count < 3:
                raise ValueError("fail")
            return "ok"

        needs_three_tries()
        expected_calls = [call(1), call(2)]
        self.assertEqual(mock_sleep.call_args_list, expected_calls)

    @patch("time.sleep")
    def test_custom_times_parameter(self, mock_sleep):
        attempt_count = 0

        @retry(times=5, delay=1, exceptions=(ValueError,))
        def needs_five_tries():
            nonlocal attempt_count
            attempt_count = attempt_count + 1
            if attempt_count < 5:
                raise ValueError("keep trying")
            return "final win"

        output = needs_five_tries()
        self.assertEqual(output, "final win")
        self.assertEqual(mock_sleep.call_count, 4)

if __name__ == "__main__":
    unittest.main()