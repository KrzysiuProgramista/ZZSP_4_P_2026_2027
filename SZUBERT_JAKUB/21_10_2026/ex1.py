import time
from contextlib import contextmanager

class TimerClass:

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"[Class Timer] Elapsed time: {time.time() - self.start:.4f} s")

        if exc_type is ValueError:
            # -------------------------------------------------------------
            # Returning True suppresses the exception, making Python think the
            # error has been fully handled. This hides bugs, prevents calling
            # code from knowing that a failure occurred, and can leave the
            # application in an unpredictable state. It should only be done
            # when there is a very deliberate recovery mechanism.
            # -------------------------------------------------------------
            print(f"[Class Timer] Suppressed exception: {exc_val}")
            return True

        return False

@contextmanager
def timer_generator():
    start = time.time()
    try:
        yield
    except ValueError as e:
        print(f"[Generator Timer] Suppressed exception: {e}")
    finally:
        print(f"[Generator Timer] Elapsed time: {time.time() - start:.4f} s")


if __name__ == "__main__":
    print("--- Testing Class Timer ---")
    with TimerClass():
        time.sleep(0.3)

    print("\n--- Testing Generator Timer ---")
    with timer_generator():
        time.sleep(0.3)

    print("\n--- Testing Exception Suppression (Class) ---")
    with TimerClass():
        time.sleep(0.1)
        raise ValueError("Something went wrong in the class!")
    print("Execution continued because the ValueError was suppressed.\n")

    print("--- Testing Exception Suppression (Generator) ---")
    with timer_generator():
        time.sleep(0.1)
        raise ValueError("Something went wrong in the generator!")
    print("Execution continued because the ValueError was suppressed.")