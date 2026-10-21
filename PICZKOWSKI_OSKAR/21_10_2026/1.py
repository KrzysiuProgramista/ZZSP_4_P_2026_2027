from contextlib import contextmanager
import time



class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        print("Timer started")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self.start
        print(f"Timer stopped: {elapsed:.6f} seconds")

       
        if exc_type is ZeroDivisionError:
            return True

        return False


# 2. The same Timer using @contextmanager
@contextmanager
def timer():
    start = time.perf_counter()
    print("Timer started")

    try:
        yield
    except ZeroDivisionError:
     
        pass
    finally:
        elapsed = time.perf_counter() - start
        print(f"Timer stopped: {elapsed:.6f} seconds")




print("Class-based Timer:")
with Timer():
    time.sleep(0.1)

print("\nGenerator-based Timer:")
with timer():
    time.sleep(0.1)



print("\nClass-based Timer with ZeroDivisionError:")
with Timer():
    1 / 0
print("Program continues")


print("\nGenerator-based Timer with ZeroDivisionError:")
with timer():
    1 / 0
print("Program continues")