import functools
import time

# ==========================================
# Exercise 6: Stacking
# ==========================================

# Modyfikujemy dekoratory tak, by dokładnie pokazywały "wejście" i "wyjście"
def logged(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  [LOGGED] Entering {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"  [LOGGED] Exiting {func.__name__}. Result: {result}")
        return result
    return wrapper

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"  [TIMER] Timer started for {func.__name__}...")
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"  [TIMER] Timer finished. {func.__name__} took {end - start:.4f}s")
        return result
    return wrapper

# STACK 1: @logged on top, @timer on bottom
@logged
@timer
def slow_add_1(a, b):
    print("      -> slow_add_1 is executing body...")
    time.sleep(0.2)
    return a + b

# STACK 2: @timer on top, @logged on bottom
@timer
@logged
def slow_add_2(a, b):
    print("      -> slow_add_2 is executing body...")
    time.sleep(0.2)
    return a + b


if __name__ == "__main__":
    print("==========================================")
    print("STACKING DECORATORS TEST")
    print("==========================================")
    
    print("\n1. Order: @logged -> @timer -> function")
    print("Prediction: \n - LOGGED is the outermost wrapper, it will run first.\n - LOGGED calls TIMER.\n - TIMER starts clock, calls the actual function.\n - TIMER finishes clock.\n - LOGGED finishes and prints result.\n")
    slow_add_1(2, 3)
    
    print("\n" + "="*40 + "\n")
    
    print("2. Order: @timer -> @logged -> function")
    print("Prediction: \n - TIMER is the outermost wrapper, it will run first and start the clock.\n - TIMER calls LOGGED.\n - LOGGED prints entering and calls actual function.\n - LOGGED prints exiting.\n - TIMER finishes the clock (which now includes the time taken by LOGGED as well).\n")
    slow_add_2(4, 5)

"""
WNIOSEK (Stacking Order):
=========================
Dekoratory w Pythonie aplikowane są od "dołu do góry", co oznacza:
@A
@B
def func(): ... 
... to w rzeczywistości A(B(func)).

Dlatego z perspektywy wywołania kodu, wchodzi on w to z "zewnątrz do wewnątrz" 
(Top to Bottom). Funkcja na samej górze (zewnętrzna) uruchamia swój kod 
przed wywołaniem inner function (zanim wpadnie niżej na stosie).
"""