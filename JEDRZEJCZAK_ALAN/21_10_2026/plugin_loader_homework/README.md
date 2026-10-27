# Exercise 4: Python plugin loader

A complete homework solution using only the Python standard library. Requires
Python **3.9 or newer**. No packages need to be installed.

## Run

Open a terminal in this project folder:

```console
python main.py
python -m unittest discover -s tests -v
```

On Windows, `py -3.13` can replace `python` if you want to select that installed
Python version. The test suite contains exactly **10 test methods**; some use
subtests for several related cases.

The demo discovers `numbers.py`, `summary.py`, and `words.py`. They return an
integer, a dictionary with a nested list, and a string. The results are formatted
by `singledispatch`, and all plugin cleanup hooks run before the program finishes.

## Files

```text
plugin_loader_homework/
    plugin_loader.py         # Loader, interface, metadata, result handlers
    main.py                  # Runnable demo
    plugins/
        numbers.py
        summary.py
        words.py
    tests/
        test_plugin_loader.py
    CONTEXT_MANAGERS.md      # Explanation linked to exercises 1, 2, 3, and 4
    README.md
```

## How the requirements are implemented

| Requirement | Implementation |
| --- | --- |
| Runtime discovery | `PluginLoader.discover()` rescans the folder for public, top-level `.py` files and sorts them |
| Interface validation | Each module exports `PLUGIN_CLASS`, a concrete `Plugin` subclass with valid metadata, a constructor requiring no arguments, and callable hooks requiring no arguments |
| Context manager and cleanup | `PluginLoader.load()` uses `@contextmanager` and `ExitStack`; callbacks run in reverse order on success or failure |
| Immutable metadata | `PluginMetadata` is a frozen dataclass with string fields |
| Different result types | `format_result()` uses `@singledispatch` for strings, integers, floats, booleans, `None`, lists, and dictionaries |
| Cached initialization | `Plugin.resource` uses `@cached_property` and calls `initialize()` once per instance until the cache is cleared |
| Tests | Exactly 10 `unittest` methods, including a failed setup followed by successful recovery |

## Plugin interface

Each plugin module exports its class as `PLUGIN_CLASS`. The class must inherit
from `Plugin` and provide `metadata`, `initialize()`, and `run()`. The base class
supplies `setup()` and `cleanup()`; a plugin may override them.

Save this as `plugins/hello.py` and run the demo again:

```python
from plugin_loader import Plugin, PluginMetadata


class HelloPlugin(Plugin):
    metadata = PluginMetadata("hello", "1.0", "A greeting plugin")

    def initialize(self):
        # Put an expensive calculation or resource creation here.
        return "Hello from a plugin!"

    def run(self):
        return self.resource


PLUGIN_CLASS = HelloPlugin
```

No loader changes are needed when another plugin file is added. Files whose stems
start with `_`, such as `__init__.py` or `_helpers.py`, are ignored. Discovery is
flat: nested folders are not scanned.

## Lifetime and failures

```python
from pathlib import Path
from plugin_loader import PluginLoader, format_result


loader = PluginLoader(Path("plugins"))
with loader.load() as plugins:
    for plugin in plugins:
        print(format_result(plugin.run()))
# All registered cleanup hooks have run here.
```

For each module the loader imports it, validates the class, constructs and
validates an instance, registers its cleanup, and calls `setup()`. Default setup
accesses `resource`, so the expensive initialization happens inside the protected
lifetime. Repeated accesses reuse that instance's cached value.

The collection is yielded only after every plugin is ready. If plugin B fails in
setup after plugin A loaded, B's cleanup runs first, then A's. The body of `with`
does not execute. Temporary entries created by the loader in `sys.modules` are
also removed, including after failed imports. Python modules imported as
dependencies are left to Python's normal import cache.

The caller receives `PluginValidationError` for an invalid interface or
`PluginLoadError` for an import, construction, or setup error. The original error
is retained as `__cause__`. Exceptions from the `with` body propagate after
cleanup. The same loader can be used again by calling `load()` again after the
faulty plugin is fixed or removed. Each call creates fresh plugin instances.

A plugin that opens files, sockets, or other external resources must override
`cleanup()` to release them. Base cleanup only discards the cached value. Cleanup
must tolerate partial setup; for example, store an opened file on `self` before
performing later work that may fail, and use `getattr(self, "file", None)` during
cleanup. If acquisition fails before a value is cached, `cached_property` cannot
recover that partial resource for you.

Module imports and constructors must avoid acquiring unmanaged resources: an
instance's cleanup can only be registered after successful construction and
validation. Plugins execute trusted Python code; this loader is not a sandbox.
If one cleanup hook raises, `ExitStack` still attempts the remaining callbacks.
That cleanup exception may become the propagated error, with earlier exceptions
in its exception chain.

## Tests

The tests cover discovery, valid loading, interface and metadata validation,
frozen metadata, normal and exceptional cleanup, recovery after loading failure,
the initialization cache, and result dispatch. Temporary plugin folders keep the
tests independent of the demo plugins. Run them with:

```console
python -m unittest discover -s tests -v
```

Read [CONTEXT_MANAGERS.md](CONTEXT_MANAGERS.md) for the context manager explanation
and references to the original class exercises.
