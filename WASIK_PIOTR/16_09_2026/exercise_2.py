import functools
import time
import unittest
from unittest.mock import call, patch


def retry(
    times=3,
    delay=1,
    backoff=1,
    exceptions=(Exception,),
):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        print(
                            f"[RETRY LOG] Próba {attempt}/{times} nie powiodła się z błędem '{e}'. Brak kolejnych prób."
                        )
                        raise

                    print(
                        f"[RETRY LOG] Próba {attempt}/{times} nie powiodła się ({e}). Ponawiam za {current_delay:.2f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator


attempt_counter = 0


@retry(times=5, delay=0.5, backoff=2, exceptions=(ValueError,))
def unstable():
    global attempt_counter
    attempt_counter += 1
    if attempt_counter < 3:
        raise ValueError("Chwilowy błąd połączenia/usługi")
    return "Sukces! Funkcja zwróciła poprawny wynik."


class TestRetryDecorator(unittest.TestCase):

    @patch("time.sleep")
    def test_succeeds_immediately(self, mock_sleep):
        @retry(times=3, delay=1)
        def always_succeeds():
            return "ok"

        result = always_succeeds()
        self.assertEqual(result, "ok")
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_fails_twice_then_succeeds(self, mock_sleep):
        calls = 0

        @retry(times=5, delay=1)
        def fails_twice():
            nonlocal calls
            calls += 1
            if calls < 3:
                raise ValueError("Fail")
            return "success"

        result = fails_twice()
        self.assertEqual(result, "success")
        self.assertEqual(calls, 3)
        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_exceeds_max_attempts_and_raises(self, mock_sleep):
        @retry(times=3, delay=1)
        def always_fails():
            raise RuntimeError("Fatal error")

        with self.assertRaises(RuntimeError):
            always_fails()

        self.assertEqual(mock_sleep.call_count, 2)

    @patch("time.sleep")
    def test_exponential_backoff(self, mock_sleep):
        @retry(times=4, delay=1, backoff=2)
        def always_fails():
            raise ValueError("Fail")

        with self.assertRaises(ValueError):
            always_fails()

        expected_calls = [call(1), call(2), call(4)]
        mock_sleep.assert_has_calls(expected_calls)
        self.assertEqual(mock_sleep.call_count, 3)

    @patch("time.sleep")
    def test_specific_exceptions_caught(self, mock_sleep):
        @retry(times=3, delay=1, exceptions=(ValueError,))
        def throws_key_error():
            raise KeyError("Inny błąd")

        with self.assertRaises(KeyError):
            throws_key_error()

        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_preserves_function_metadata(self, mock_sleep):
        @retry(times=3)
        def dummy_function():
            """Docstring funkcji testowej."""
            pass

        self.assertEqual(dummy_function.__name__, "dummy_function")
        self.assertEqual(dummy_function.__doc__, "Docstring funkcji testowej.")


if __name__ == "__main__":
    res = unstable()
    print(f"Wynik: {res}\n")
    unittest.main(verbosity=2)