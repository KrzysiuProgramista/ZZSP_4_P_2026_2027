# Context Managers and Plugin Loader

## What is a context manager?

A context manager sets up a resource before a `with` block and reliably cleans it up
when the block ends. Cleanup happens even when an exception is raised. The usual
protocol is `__enter__()` and `__exit__()`, or the `@contextmanager` decorator from
`contextlib`.

## Exercise 1 — timing

`Timer` implements `__enter__` and `__exit__` as a class. The `timer()` generator
uses `@contextmanager` and a `try/finally` block. Both measure the time spent inside
the `with` block. The class-based example suppresses `ValueError` by returning
`True` from `__exit__`; this is usually a bad idea because it can hide a real failure
and allow the program to continue with incorrect assumptions.

Run:

```bash
python exercise1.py
```

## Exercise 2 — managing resources

- `database_transaction(connection)` commits after success and rolls back when an
  exception occurs.
- `temporary_directory()` removes the temporary folder in `finally`.
- `working_directory(path)` restores the previous current directory.
- `temporary_environment(name, value)` restores the previous environment value,
  or removes the variable if it did not exist before.

Run:

```bash
python exercise2.py
```

## Exercise 3 — nesting and combining managers

- A single `with` statement can manage a temporary directory and a file together.
- `ExitStack` manages a variable number of files and closes already-opened files
  if opening a later file fails.
- `suppress(FileNotFoundError)` is a concise equivalent to catching that exception
  and doing nothing.
- `closing()` adapts an object with `close()` but no context-manager protocol.

Run:

```bash
python exercise3.py
```

## Plugin Loader project

The loader discovers `.py` modules at runtime, validates frozen dataclass metadata
and the `load()` / `run(value)` interface, and cleans up already-loaded plugins if
a later plugin fails. `handle_result()` uses `singledispatch` for strings, integers,
lists, and dictionaries. `LoadedPlugin.expensive_initialisation` demonstrates
`cached_property`.

The included `failing_plugin.py` is intentionally a failing example. It is useful
for demonstrating recovery, but the main loader aborts the load operation and closes
previously loaded plugins rather than silently skipping the broken plugin.

Run the tests from this directory:

```bash
python -m unittest discover -s tests -v
```

## Notes

The exercises use only the Python standard library. The database example uses SQLite
in-memory storage, so no separate database server is required.
