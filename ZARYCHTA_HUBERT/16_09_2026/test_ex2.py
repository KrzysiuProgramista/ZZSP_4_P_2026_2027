"""Exactly six retry tests. Every test mocks sleep; no real waits occur.

From this directory, run: python -m unittest test_ex2 -v
"""

import unittest
from unittest.mock import call, patch

from ex2 import LOGGER, retry


class RetryTests(unittest.TestCase):
    @patch("ex2.time.sleep")
    def test_success_on_first_call_does_not_sleep_or_log(self, sleep):
        calls = 0

        @retry()
        def immediate():
            nonlocal calls
            calls += 1
            return 42

        with patch.object(LOGGER, "warning") as warning:
            self.assertEqual(immediate(), 42)
        self.assertEqual(calls, 1)
        sleep.assert_not_called()
        warning.assert_not_called()

    @patch("ex2.time.sleep")
    def test_two_failures_then_success_backoff_logs_and_metadata(self, sleep):
        calls = 0

        def unstable():
            """A function that eventually works."""
            nonlocal calls
            calls += 1
            if calls < 3:
                raise ValueError("temporary problem")
            return "success"

        wrapped = retry(times=5, delay=0.5, exceptions=(ValueError,))(unstable)
        with self.assertLogs(LOGGER, level="WARNING") as logs:
            self.assertEqual(wrapped(), "success")
        self.assertEqual(calls, 3)
        self.assertEqual(sleep.call_args_list, [call(0.5), call(1.0)])
        self.assertEqual(len(logs.output), 2)
        self.assertIn("attempt 1/5", logs.output[0])
        self.assertIn("retry 1/4 in 0.5 s", logs.output[0])
        self.assertIn("retry 2/4 in 1 s", logs.output[1])
        self.assertEqual(wrapped.__name__, unstable.__name__)
        self.assertEqual(wrapped.__doc__, unstable.__doc__)
        self.assertIs(wrapped.__wrapped__, unstable)

    @patch("ex2.time.sleep")
    def test_exhaustion_reraises_final_exception_without_extra_sleep(self, sleep):
        errors = [ValueError(f"failure {n}") for n in range(4)]
        calls = 0

        @retry(times=4, delay=0.25, backoff=3, exceptions=(ValueError,))
        def always_fails():
            nonlocal calls
            error = errors[calls]
            calls += 1
            raise error

        with self.assertLogs(LOGGER, level="WARNING") as logs:
            with self.assertRaises(ValueError) as caught:
                always_fails()
        self.assertIs(caught.exception, errors[-1])
        self.assertEqual(calls, 4)
        self.assertEqual(sleep.call_args_list, [call(0.25), call(0.75), call(2.25)])
        self.assertEqual(len(logs.output), 3)

    @patch("ex2.time.sleep")
    def test_configured_exception_tuple_includes_subclasses(self, sleep):
        class TemporaryValueError(ValueError):
            pass

        errors = iter((TemporaryValueError("bad value"), OSError("busy"), None))

        @retry(times=3, delay=0.1, exceptions=(ValueError, OSError))
        def different_failures():
            error = next(errors)
            if error is not None:
                raise error
            return "done"

        with self.assertLogs(LOGGER, level="WARNING"):
            self.assertEqual(different_failures(), "done")
        self.assertEqual(sleep.call_args_list, [call(0.1), call(0.2)])

    @patch("ex2.time.sleep")
    def test_unlisted_exception_is_not_retried(self, sleep):
        calls = 0
        error = TypeError("not a temporary ValueError")

        @retry(times=5, exceptions=(ValueError,))
        def wrong_type():
            nonlocal calls
            calls += 1
            raise error

        with patch.object(LOGGER, "warning") as warning:
            with self.assertRaises(TypeError) as caught:
                wrong_type()
        self.assertIs(caught.exception, error)
        self.assertEqual(calls, 1)
        sleep.assert_not_called()
        warning.assert_not_called()

    @patch("ex2.time.sleep")
    def test_arguments_are_forwarded_and_constant_backoff_is_supported(self, sleep):
        received = []

        @retry(times=3, delay=0.2, backoff=1, exceptions=(ValueError,))
        def add(a, b, *, scale=1):
            received.append((a, b, scale))
            if len(received) < 3:
                raise ValueError("try again")
            return (a + b) * scale

        with self.assertLogs(LOGGER, level="WARNING"):
            self.assertEqual(add(2, 3, scale=4), 20)
        self.assertEqual(received, [(2, 3, 4)] * 3)
        self.assertEqual(sleep.call_args_list, [call(0.2), call(0.2)])


if __name__ == "__main__":
    unittest.main()
