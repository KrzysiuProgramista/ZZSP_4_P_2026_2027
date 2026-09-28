import functools
import time

# ==========================================
# Exercise 5: Class decorators and decorating methods
# ==========================================

# Pomocniczy dekorator timer (znany z wcześniejszych zadań)
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f" [TIMER] {func.__name__} executed in {end - start:.4f} seconds.")
        return result
    return wrapper

# 1. Dekorator dla metod
def log_method(func):
    """
    Decorator that works on a method. 
    It knows that the first argument is 'self' and prints the class name.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        class_name = self.__class__.__name__
        print(f" [LOG] Calling method '{func.__name__}' from instance of '{class_name}'")
        return func(self, *args, **kwargs)
    return wrapper

# 2. Dekorator klasy aplikujący @timer do każdej metody
def time_all_methods(cls):
    """
    Class decorator that applies the @timer decorator to all of its methods.
    """
    for attr_name, attr_value in vars(cls).items():
        # Szukamy metod, omijając 'magic methods' (jak __init__)
        if callable(attr_value) and not attr_name.startswith("__"):
            # Zastępujemy oryginalną metodę - metodą udekorowaną
            setattr(cls, attr_name, timer(attr_value))
    return cls

# 3. Komentarz porównujący z metaklasami:
"""
COMPARISON: Class Decorators vs Metaclasses
-------------------------------------------
Applying decorators to all methods of a class can be done using a class decorator 
(as above) or via a Metaclass (overriding __new__ or __init__ of the type).

Readability: 
Class decorators are generally MUCH MORE READABLE and easier to understand. 
A class decorator is simply a function that takes a class object, modifies it 
(e.g., looping through its __dict__ and wrapping callables), and returns it. 

Metaclasses, on the other hand, hook deeply into the class creation mechanism. 
They are inherently complex and abstract. According to Python's philosophy, 
"Simple is better than complex". For simple tasks like modifying existing attributes, 
class decorators are the superior and more readable choice. Metaclasses should 
be reserved for complex API designs where you actually need to control how the 
class object itself is instantiated.
"""

# ==========================================
# Testing Exercise 5
# ==========================================
if __name__ == "__main__":
    @time_all_methods
    class DataProcessor:
        def __init__(self, data):
            self.data = data
            
        @log_method # Metoda może mieć dodatkowy, własny dekorator
        def process_fast(self):
            time.sleep(0.1)
            return len(self.data)

        def process_slow(self):
            time.sleep(0.3)
            return sum(self.data)

    print("--- Testing Class and Method Decorators ---")
    processor = DataProcessor([1, 2, 3, 4, 5])
    
    processor.process_fast()
    processor.process_slow()