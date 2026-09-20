import unittest
from unittest.mock import patch, call
from ex2 import retry

class TestRetryDecorator(unittest.TestCase):

    @patch("time.sleep")
    def test_1_succeeds_after_failing_twice(self, mock_sleep):
        """1. Retries and succeeds after failing twice."""
        attempts = 0

        @retry(times=5, delay=0.5, backoff=1.0, exceptions=(ValueError,))
        def unstable():
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary failure")
            return "Success"

        result = unstable()

        self.assertEqual(result, "Success")
        self.assertEqual(attempts, 3)
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_has_calls([call(0.5), call(0.5)])

    @patch("time.sleep")
    def test_2_exceeds_max_retries_and_raises(self, mock_sleep):
        """2. Exhausts all attempts and re-raises the final exception."""
        attempts = 0

        @retry(times=3, delay=1.0)
        def always_fails():
            nonlocal attempts
            attempts += 1
            raise RuntimeError("Persistent crash")

        with self.assertRaises(RuntimeError):
            always_fails()

        self.assertEqual(attempts, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_3_exponential_backoff(self, mock_sleep):
        """3. Increases sleep delay exponentially on successive failures."""
        @retry(times=4, delay=1.0, backoff=2.0)
        def always_fails():
            raise ValueError("Failure")

        with self.assertRaises(ValueError):
            always_fails()

        expected_calls = [call(1.0), call(2.0), call(4.0)]
        mock_sleep.assert_has_calls(expected_calls)
        self.assertEqual(mock_sleep.call_count, 3)

    @patch("time.sleep")
    def test_4_catches_only_specified_exceptions(self, mock_sleep):
        """4. Retries specified exceptions (ValueError) but raises non-matching exceptions (KeyError) immediately."""
        attempts = 0

        @retry(times=3, delay=1.0, exceptions=(ValueError,))
        def raises_key_error():
            nonlocal attempts
            attempts += 1
            raise KeyError("Uncaught exception")

        with self.assertRaises(KeyError):
            raises_key_error()

        self.assertEqual(attempts, 1)
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_5_logs_retry_attempts(self, mock_sleep):
        """5. Emits warning logs for every failed attempt."""
        @retry(times=3, delay=0.5, exceptions=(ValueError,))
        def fails_twice():
            raise ValueError("Test error log")

        with self.assertLogs("retry_decorator", level="WARNING") as log_context:
            with self.assertRaises(ValueError):
                fails_twice()

        self.assertEqual(len(log_context.output), 3)
        self.assertTrue(any("Attempt 1/3 failed" in msg for msg in log_context.output))
        self.assertTrue(any("Attempt 2/3 failed" in msg for msg in log_context.output))
        self.assertTrue(any("Exhausted all retries" in msg for msg in log_context.output))

    @patch("time.sleep")
    def test_6_preserves_metadata_and_arguments(self, mock_sleep):
        """6. Preserves function metadata (__name__, __doc__) and accepts positional/keyword args."""
        @retry(times=2, delay=0.1)
        def multiply(x, y, factor=1):
            """Multiplies two numbers by a factor."""
            return (x * y) * factor

        result = multiply(3, 4, factor=2)

        self.assertEqual(result, 24)
        self.assertEqual(multiply.__name__, "multiply")
        self.assertEqual(multiply.__doc__, "Multiplies two numbers by a factor.")
        mock_sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()