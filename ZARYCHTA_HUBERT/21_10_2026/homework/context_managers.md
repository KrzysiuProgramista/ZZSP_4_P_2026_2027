# Context managers in Python

A context manager controls what happens when a block of code starts and finishes.
It is normally used with the `with` statement. It helps manage resources such as
files and database connections, but it can also measure time or temporarily
change a setting.

The main idea is to keep setup and cleanup together. This avoids repeating
cleanup code and makes it run when the block finishes, including when an
exception occurs.

```python
with open("example.txt", "w", encoding="utf-8") as file:
    file.write("Hello!")
# The file is now closed.
```

For this file example, the same cleanup can be written explicitly:

```python
file = open("example.txt", "w", encoding="utf-8")
try:
    file.write("Hello!")
finally:
    file.close()
```

## How `with` works

A class-based context manager implements two methods:

- `__enter__()` performs setup. Its return value is assigned to the variable
  after `as`.
- `__exit__(exc_type, exc_value, traceback)` performs cleanup after the block.
  The three arguments describe an exception, or are all `None` if the block
  finished normally.

If `__exit__()` returns a truthy value, the exception is suppressed. Returning
`False` or `None` lets it propagate. Suppression does not resume execution at the
failed statement: execution continues after the `with` block.

Cleanup also happens when leaving the block using `return`, `break` or
`continue`. However, if `__enter__()` itself fails, Python does not call that
manager's `__exit__()`. Setup must therefore clean up any resources acquired
before it fails. Context managers also cannot guarantee cleanup after a forced
process termination.

## Exercise 1: Two ways to write a timer

Source: [exercise1.py](https://github.com/KrzysiuProgramista/ZZSP_4_P_2026_2027/blob/main/ZARYCHTA_HUBERT/21_10_2026/exercise1.py)

### Class-based timer

In `Timer`, `__enter__()` saves the current value of `perf_counter()` and returns
`self`. `__exit__()` calculates and prints the elapsed time.

```python
with Timer() as class_timer:
    sleep(0.1)

print(class_timer.elapsed)
```

`class_timer` is the object returned by `__enter__()`. Its `elapsed` attribute is
set when the block ends. `perf_counter()` is suitable for measuring durations.

The implementation returns `True` when `exc_type is ValueError`. This suppresses
that exact exception type; other exception types propagate. Hiding exceptions
can make debugging difficult and allow a program to continue with invalid state,
so suppression should be intentional and narrow.

### Generator-based timer

The same setup/cleanup pattern can be written using `@contextmanager`:

```python
@contextmanager
def timer():
    result = {}
    start = perf_counter()
    try:
        yield result
    finally:
        result["elapsed"] = perf_counter() - start
        print(f"Elapsed: {result['elapsed']:.4f} s")
```

Code before `yield` performs setup. The yielded value becomes the variable after
`as`. When the block ends, execution resumes in the generator. An exception in
the block is raised at the `yield` point, so `finally` is needed to ensure cleanup.
A generator used with `@contextmanager` must yield exactly once.

```python
with timer() as generator_timer:
    sleep(0.1)

print(generator_timer["elapsed"])
```

Both implementations measure elapsed time, but they are not identical in every
respect: the class exposes an attribute and suppresses `ValueError`, while the
generator uses a dictionary and lets exceptions propagate. The assertions in
Exercise 1 check that both durations are at least 0.1 seconds; they do not prove
identical exception handling or identical measured times.

## Exercise 2: Managing resources and restoring state

Source: [exercise2.py](https://github.com/KrzysiuProgramista/ZZSP_4_P_2026_2027/blob/main/ZARYCHTA_HUBERT/21_10_2026/exercise2.py)

| Context manager | Setup | Work on exit |
| --- | --- | --- |
| `database_connection(path)` | Open a SQLite connection | Commit on success, roll back on failure, and close the connection |
| `temporary_directory()` | Create a temporary directory | Remove the directory and its contents |
| `working_directory(path)` | Remember the current directory and switch to another | Restore the previous directory |
| `environment_variable(name, value)` | Remember the old value and set a temporary value | Restore the old value, or remove the variable if it was previously absent |

For example, the database context manager yields a connection for the block:

```python
with database_connection(database) as connection:
    connection.execute("INSERT INTO users VALUES (?)", ("Hubert",))
```

If the block succeeds, execution continues after `yield` and calls `commit()`.
If the block raises, the exception handler calls `rollback()` and re-raises the
exception. The `finally` block closes the connection in either case. Closing is
also attempted if committing or rolling back raises an exception.

The demonstration inserts `"Hubert"` successfully, then deliberately raises an
error after inserting `"Rolled back"`. The later query verifies that the failed
insertion was not saved.

The other managers show that cleanup can mean restoring previous state, not just
closing a resource. Changes to the working directory and environment variables
affect the whole process, so overlapping use in different threads needs care.

## Exercise 3: Combining context managers

Source: [exercise3.py](https://github.com/KrzysiuProgramista/ZZSP_4_P_2026_2027/blob/main/ZARYCHTA_HUBERT/21_10_2026/exercise3.py)

### Multiple managers in one statement

```python
with open(source_path, encoding="utf-8") as source, open(
    target_path, "w", encoding="utf-8"
) as target:
    target.write(source.read())
```

Managers are entered from left to right and exited from right to left. Here,
`target` closes before `source`. If opening `target` fails, the already opened
`source` is still closed. This behaves like nested `with` statements.

### `ExitStack`: A variable number of resources

When the number of resources is only known at runtime, `ExitStack` manages them
dynamically:

```python
with ExitStack() as stack:
    files = [stack.enter_context(open(path, encoding="utf-8")) for path in paths]
    for file in files:
        print(file.read())
```

`enter_context()` enters each manager and registers its exit operation. The stack
exits registered managers in reverse order. If opening a later file fails,
earlier files are still closed. An empty list of paths also works.

### `suppress`: Ignoring a specific expected exception

```python
with suppress(FileNotFoundError):
    missing_file.unlink()
```

For this operation, it has the same purpose as:

```python
try:
    missing_file.unlink()
except FileNotFoundError:
    pass
```

Both ignore a missing file but let unrelated errors propagate. `try/except` is
more useful when the handler needs to log, recover or perform another action.

### `closing`: Adapting an object with `close()`

The `Resource` class has a `close()` method but does not implement the context
manager protocol. `closing()` provides that protocol:

```python
with closing(Resource()) as resource:
    resource.use()
```

It calls `resource.close()` when the block ends, including on an exception.
It does not suppress the exception.

## Connection to the plugin loader

The plugin loader uses the same principles: entering a session loads and
initializes plugins, while leaving it releases their registered resources.
`ExitStack` fits this task because the number of plugins is discovered at
runtime. Cleanup must be registered before a later initialization step can fail,
so a failed plugin can trigger cleanup of both its partial setup and previously
loaded plugins.
