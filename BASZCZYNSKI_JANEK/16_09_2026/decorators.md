A decorator is basically a function that wraps another function to run code
before or after it without touching the original code. It is mainly used for
things like timing, logging, and access checks.

Why this works in Python: Functions are treated as first-class objects. You can
pass them around and store them just like strings or numbers.

Storing a function in a variable: def greet(user): return f"Welcome, {user}!"

my_func = greet print(my_func("Sam"))

Passing a function into another function: def run_func(f, value): return
f(value)

print(run_func(greet, "Alex"))

Returning a function from inside another function: def get_multiplier(factor):
def multiply(number): return number * factor return multiply

double = get_multiplier(2) print(double(5))

How a basic decorator works: You define a wrapper function inside, call the
original function in the middle, and return the wrapper.

def announcement_decorator(func): def wrapper(): print("[Starting Task]") func()
print("[Task Finished]") return wrapper

def send_alert(): print("System status: Normal.")

send_alert = announcement_decorator(send_alert) send_alert()

The @ syntax shortcut: Writing send_alert = announcement_decorator(send_alert)
manually is messy. Python lets you use the @ symbol above the definition
instead. It does the exact same thing:

@announcement_decorator def send_alert(): print("System status: Normal.")

send_alert()

Handling arguments and return values: If the decorated function takes parameters
or returns a value, the wrapper needs *args and **kwargs so it doesn't break,
and it must explicitly return the result.

def log_execution(func): def wrapper(*args, **kwargs): print(f"Calling function
with arguments: {args}") result = func(*args, **kwargs) print("Finished
execution") return result return wrapper

@log_execution def calculate_tax(amount, rate=0.2): return amount * rate

total_tax = calculate_tax(100, rate=0.25) print(f"Tax: {total_tax}")

Important gotcha: preserving function identity When you decorate a function,
Python replaces its name and docstring with the wrapper's details. To keep the
original function name and info intact, always use @functools.wraps:

import functools

def clean_decorator(func): @functools.wraps(func) def wrapper(*args, **kwargs):
return func(*args, **kwargs) return wrapper

@clean_decorator def process_data(): """Processes user data.""" pass

print(process_data.name) print(process_data.doc)

Standard reusable template:

import functools

def my_decorator(func): @functools.wraps(func) def wrapper(*args, **kwargs):
output = func(*args, **kwargs) return output return wrapper

Where this is actually used in real projects: Timing: measuring execution speed
using time.perf_counter. Logging: tracking inputs and outputs automatically.
Authorization: checking user login permissions before running a view in Flask or
Django. Caching: storing expensive function outputs using lru_cache so they do
not have to recalculate.
