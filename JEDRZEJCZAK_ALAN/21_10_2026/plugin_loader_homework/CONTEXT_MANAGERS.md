# Context managers: from exercises 1–3 to the plugin loader

## The idea

A context manager controls a temporary situation: acquire a resource or change some state, use it, and then clean up. Python's `with` statement makes the lifetime of that situation visible in the code.

```python
with open("notes.txt", "w", encoding="utf-8") as file:
    file.write("Hello!\n")
# The file is closed here, including if file.write() raised an exception.
```

Resources include files, database connections, temporary directories, and plugins. Temporary state includes a changed working directory or environment variable. Cleanup also runs when the body exits through `return`, `break`, or `continue`.

This is structured cleanup, not a promise that cleanup can survive a forcibly terminated process or repair a broken cleanup function.

## Two ways to write a context manager

### A class: `__enter__` and `__exit__`

```python
class MessageScope:
    def __enter__(self):
        print("Starting")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Finishing")
        return False


with MessageScope() as scope:
    print("Working")
```

Python calls `__enter__()` before the body. Its return value becomes the variable after `as`; that value need not be the manager itself. After the body, Python calls `__exit__()` with information about any exception. On normal completion, all three exception arguments are `None`.

Returning `False` or `None` allows an exception to propagate. Returning a truthy value suppresses it, so execution continues after the `with` statement. Cleanup and suppression are separate choices: releasing resources usually should not hide the original failure.

One important limit: if `__enter__()` raises, Python does **not** call that manager's `__exit__()`. Entry code must therefore arrange cleanup for resources acquired before entry finishes.

### A generator: `@contextmanager`

For a short acquire/use/release sequence, `contextlib.contextmanager` avoids writing a class:

```python
from contextlib import contextmanager


@contextmanager
def message_scope():
    print("Starting")
    try:
        yield "ready"
    finally:
        print("Finishing")


with message_scope() as status:
    print(status)
```

Code before `yield` performs entry. The yielded value becomes `status`. The generator resumes when the body ends; if the body raised, the exception is raised at the `yield` expression. Putting cleanup in `finally` makes it run on both paths. There must be exactly one yield on a successful entry.

Code placed only after `yield`, outside `finally`, can be skipped by an exception. Likewise, catching an exception without raising it again suppresses it. Use a bare `raise` after logging when the caller should still see the error.

A class is useful when the manager has several methods or substantial state. A generator often makes a small lifetime easier to read. Each call to a decorated generator function creates a new manager; do not reuse the same returned manager instance.

## Exercise 1: timers and exception suppression

[exercise1.py](https://github.com/KrzysiuProgramista/ZZSP_4_P_2026_2027/blob/main/JEDRZEJCZAK_ALAN/21_10_2026/exercise1.py) demonstrates both styles:

- `Timer.__enter__()` records `time.perf_counter()`, and `__exit__()` prints the elapsed time. It returns `False`, so failures still reach the caller.
- The generator `timer()` records the start before `yield` and prints elapsed time in `finally`.
- `SafeTimer` first performs the timer's exit action and then returns `True` only when `exc_type is ValueError`.

That last condition matches the exact `ValueError` class. It does not match a subclass. Suppression is deliberate here; a plugin loader should normally propagate loading or execution failures after cleaning up.

## Exercise 2: resources and temporary state

[exercise2.py](https://github.com/KrzysiuProgramista/ZZSP_4_P_2026_2027/blob/main/JEDRZEJCZAK_ALAN/21_10_2026/exercise2.py) applies the same pattern to several lifetimes:

| Manager | During entry | When leaving |
| --- | --- | --- |
| `database_connection()` | Open a SQLite connection | Commit after a successful body, roll back on an `Exception` from the body, and close in `finally` |
| `temporary_directory()` | Create a temporary directory | Remove the directory and its contents |
| `change_directory()` | Save the original directory, then change it | Restore the original directory |
| `temporary_env()` | Save the previous value, then assign a temporary one | Restore the old value, or remove the key if it was absent |

The database example separates success (`else`), failure (`except`), and unconditional cleanup (`finally`). Its `except Exception` does not catch `KeyboardInterrupt` or `SystemExit`; the `finally` block still closes the connection.

Changing a directory or environment variable affects process-wide state. Restoring that state matters even when no file or connection needs closing.

## Exercise 3: combining managers with `ExitStack`

[exercise3.py](https://github.com/KrzysiuProgramista/ZZSP_4_P_2026_2027/blob/main/JEDRZEJCZAK_ALAN/21_10_2026/exercise3.py) opens two files in one `with` statement, then uses `ExitStack` for a variable number of files.

```python
from contextlib import ExitStack

filenames = ["first.txt", "second.txt"]
with ExitStack() as stack:
    files = [
        stack.enter_context(open(name, encoding="utf-8"))
        for name in filenames
    ]
    print([file.read() for file in files])
```

This snippet assumes those files exist. If opening the second file fails, the first is still closed. Exit actions run in reverse registration order: last in, first out. This resembles leaving nested `with` blocks.

`ExitStack.callback(function, *arguments)` also registers plain cleanup functions. These callbacks cannot suppress an exception by returning `True`.

The exercise also shows:

- `suppress(FileNotFoundError)`: deliberately ignore that exception type, similar to a narrow `try/except/pass`.
- `closing(resource)`: call an object's `close()` on exit, even if the object has no context manager methods.

## Exercise 4: the plugin loader homework

The linked folder contains exercises 1–3. The plugin loader in this project is exercise 4, the homework extending those ideas.

```python
from pathlib import Path
from plugin_loader import PluginLoader

folder = Path(__file__).resolve().parent / "plugins"
with PluginLoader(folder).load() as plugins:
    for plugin in plugins:
        print(plugin.run())
```

The loader discovers Python modules at runtime and validates each module's exported `PLUGIN_CLASS`. A plugin supplies the required methods and frozen `PluginMetadata`. The context manager owns the plugins' active lifetime.

The crucial ordering is:

```python
# Simplified excerpt of the resource-management pattern:
with ExitStack() as stack:
    plugin = plugin_class()
    stack.callback(plugin.cleanup)
    plugin.setup()
    # Register and set up further plugins, then yield the collection.
```

Register cleanup **before** setup. If plugin B acquires a resource and then fails during setup, the stack calls B's cleanup and then A's cleanup. The outer `with` body never starts, but the stack inside the generator still unwinds. If the body later raises, the same cleanup path runs.

The loader propagates the failure. “Recovery” means resources are released and another loading attempt can succeed; it does not mean silently pretending every plugin loaded.

The other homework features serve different purposes:

- `@dataclass(frozen=True)` protects metadata fields from reassignment. Freezing is shallow; mutable objects stored in fields would still be mutable. Here the metadata fields are strings.
- `@cached_property` computes `resource` through `initialize()` on first access and stores it on that plugin instance. Default setup accesses it, so initialization happens during loading and repeated accesses reuse the result.
- `cleanup()` releases plugin-owned resources and discards the cached value. Clearing a cache alone does not close a resource; subclasses must release what they acquired, including anything acquired before initialization raised.
- `@singledispatch` chooses a result handler using the first argument's runtime type. It handles values returned by `run()`; it does not manage resource lifetime.

Plugins are trusted Python code. Import-time code and constructors must avoid unmanaged resource acquisition because plugin cleanup can only be registered after construction succeeds. Cleanup hooks should tolerate partial setup. `ExitStack` attempts the remaining callbacks even if one raises, but a cleanup exception can become the propagated error, with the earlier error available through exception chaining.

The tests include a plugin that fails during loading, checks cleanup of its partial state and previously loaded plugins, and then verifies a successful subsequent load.
