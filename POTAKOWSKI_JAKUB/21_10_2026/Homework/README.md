# Context managers in Python

A context manager groups setup and cleanup around a block of code. The `with`
statement enters the managed scope before running the block and exits it
afterward, including when an exception is raised. This makes context managers
useful for resources that must be released reliably, such as files, network
connections, locks, and initialized plugins.

## The `with` statement

```python
with open("notes.txt", encoding="utf-8") as file:
    contents = file.read()
```

Python closes the file when the block ends, even if reading it raises an
exception. Without a context manager, cleanup would need to be written in a
`finally` block.

## Implementing a context manager

A class-based context manager implements `__enter__` and `__exit__`:

```python
class ManagedResource:
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()
        return False
```

`__enter__` prepares the resource and returns the value bound after `as`.
`__exit__` performs cleanup. Returning `False` (or `None`) allows an exception
from the block to keep propagating; return `True` only when intentionally
handling that exception.

The `contextlib.contextmanager` decorator is a concise alternative for
function-based context managers:

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    resource = acquire()
    try:
        yield resource
    finally:
        release(resource)
```

Code before `yield` is setup, and the `finally` block guarantees cleanup when
the block finishes normally or raises.

## Why the plugin loader uses one

`PluginLoader.load_plugins()` is itself a context manager. Entering it discovers
plugins, creates them, validates their interface, and initializes them. Exiting
the `with` block closes every initialized plugin, including when a later plugin
fails to initialize. For example:

```python
from plugin_loader import PluginLoader

loader = PluginLoader("plugins")
with loader.load_plugins() as plugins:
    for plugin in plugins:
        result = plugin.process("input")
        print(result)
```

This keeps plugin lifecycle cleanup next to the code that uses the plugins and
avoids leaving successfully initialized plugins open after a partial load.
