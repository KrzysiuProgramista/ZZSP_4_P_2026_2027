import functools
import inspect
import time

# ==============================================================================
# 1. DEKORATOR DLA METODY (@timer)
# ==============================================================================


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(
            f"[TIMER] Metoda '{func.__name__}' wykonała się w {end - start:.6f} s"
        )
        return result

    return wrapper


# ==============================================================================
# 2. DEKORATOR KLASY (Class Decorator)
# ==============================================================================


def time_all_methods(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if inspect.isfunction(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, timer(attr_value))
    return cls


# ==============================================================================
# 3. METAKLASA (Metaclass)
# ==============================================================================


class TimeAllMethodsMeta(type):

    def __new__(mcs, name, bases, namespace):
        for attr_name, attr_value in namespace.items():
            if inspect.isfunction(attr_value) and not attr_name.startswith(
                "__"
            ):
                namespace[attr_name] = timer(attr_value)
        return super().__new__(mcs, name, bases, namespace)


# ==============================================================================
# KLASY TESTOWE
# ==============================================================================


# Użycie dekoratora klasy
@time_all_methods
class CalculatorClassDecorator:

    def add(self, a, b):
        time.sleep(0.05)
        return a + b

    def multiply(self, a, b):
        time.sleep(0.08)
        return a * b


# Użycie metaklasy
class CalculatorMetaclass(metaclass=TimeAllMethodsMeta):

    def add(self, a, b):
        time.sleep(0.05)
        return a + b

    def multiply(self, a, b):
        time.sleep(0.08)
        return a * b


# ==============================================================================
# PUNKT WEJŚCIA I DEMONSTRACJA
# ==============================================================================

if __name__ == "__main__":
    print("--- 1. TEST DEKORATORA KLASY (@time_all_methods) ---")
    calc1 = CalculatorClassDecorator()
    print("Wynik dodawania:", calc1.add(5, 10))
    print("Wynik mnożenia:", calc1.multiply(3, 4))

    print("\n--- 2. TEST METAKLASY (metaclass=TimeAllMethodsMeta) ---")
    calc2 = CalculatorMetaclass()
    print("Wynik dodawania:", calc2.add(2, 8))
    print("Wynik mnożenia:", calc2.multiply(6, 7))


# ==============================================================================
# PORÓWNANIE CZYTELNOŚCI (PODSUMOWANIE)
# ==============================================================================
"""
PORÓWNANIE CZYTELNOŚCI (Class Decorator vs Metaclass):

1. Class Decorator (@time_all_methods) jest ZNACZNIE BARDZIEJ CZYTELNY i prostszy.
   - Składnia `@time_all_methods` bezpośrednio nad klasą jawnie wskazuje, że modyfikujemy
     istniejącą klasę.
   - Kod dekoratora działa na prostym obiekcie klasy (`cls`), pętli po jej atrybutach i `setattr`.

2. Metaklasa (TimeAllMethodsMeta) jest bardziej skomplikowana.
   - Wymaga zrozumienia cyklu życia klas w Pythonie (metody `__new__`, operowania na `namespace`).
   - Tworzy bardziej ukrytą magię (metaklasa dziedziczy się także na wszystkie podklasy,
     co może prowadzić do niechcianych efektów ubocznych lub konfliktów metaklas).

Wniosek:
Do modyfikacji lub dekorowania metod w pojedynczej klasie ZAWSZE zaleca się użycie
dekoratora klasy. Metaklasy należy stosować tylko wtedy, gdy musimy wymusić zachowanie
na całej hierarchii dziedziczenia.
"""