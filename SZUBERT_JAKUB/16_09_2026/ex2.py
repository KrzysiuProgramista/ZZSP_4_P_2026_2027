import functools
import time

def retry(times=3, delay=1, backoff=1, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"[RETRY LOG] Attempt {attempt}/{times} failed with {type(e).__name__}: {e}")
                    if attempt == times:
                        raise
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

# --- Function demonstration ---
attempt_counter = 0

@retry(times=5, delay=0.5, backoff=2, exceptions=(ValueError,))
def unstable_func():
    global attempt_counter
    attempt_counter += 1
    if attempt_counter < 3:
        raise ValueError("Temporary failure")
    return "Success!"

if __name__ == "__main__":
    print("--- Running unstable function with @retry ---")
    print(unstable_func())