import unittest
from unittest.mock import patch, call
from ex2 import retry

class TestRetryDecorator(unittest.TestCase):

    def test_1_success_first_try(self):
        calls = 0
        @retry(times=3, delay=1)
        def func():
            nonlocal calls
            calls += 1
            return "OK"

        with patch("time.sleep") as mock_sleep:
            result = func()
            self.assertEqual(result, "OK")
            self.assertEqual(calls, 1)
            mock_sleep.assert_not_called()

    def test_2_succeeds_after_failures(self):
        calls = 0
        @retry(times=3, delay=1)
        def func():
            nonlocal calls
            calls += 1
            if calls < 3:
                raise ValueError("Error")
            return "OK"

        with patch("time.sleep") as mock_sleep:
            result = func()
            self.assertEqual(result, "OK")
            self.assertEqual(calls, 3)
            self.assertEqual(mock_sleep.call_count, 2)

    def test_3_raises_exception_when_max_attempts_reached(self):
        @retry(times=3, delay=1)
        def func():
            raise ValueError("Persistent error")

        with patch("time.sleep"):
            with self.assertRaises(ValueError):
                func()

    def test_4_exponential_backoff_delays(self):
        @retry(times=4, delay=1, backoff=2)
        def func():
            raise ValueError("Error")

        with patch("time.sleep") as mock_sleep:
            try:
                func()
            except ValueError:
                pass
            # Expected delay times: 1s, 2s, 4s
            mock_sleep.assert_has_calls([call(1), call(2), call(4)])

    def test_5_handles_specified_exceptions(self):
        @retry(times=3, delay=1, exceptions=(ValueError,))
        def func():
            raise ValueError("Handled error")

        with patch("time.sleep") as mock_sleep:
            try:
                func()
            except ValueError:
                pass
            self.assertEqual(mock_sleep.call_count, 2)

    def test_6_unhandled_exceptions_raise_immediately(self):
        @retry(times=3, delay=1, exceptions=(ValueError,))
        def func():
            raise TypeError("Unhandled error type")

        with patch("time.sleep") as mock_sleep:
            with self.assertRaises(TypeError):
                func()
            mock_sleep.assert_not_called()

if __name__ == "__main__":
    unittest.main()