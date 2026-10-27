# Plugin loader homework

Python 3.10+; standard library only. Extract the ZIP and open a terminal in
`plugin_loader_homework`.

```bash
python main.py
python -m unittest -v
```

## Files
- `plugin_loader.py`: discovery, validation, metadata, context management,
  result dispatch and cached initialization.
- `plugins/greeting.py`: text result and a managed temporary file.
- `plugins/numbers.py`: expensive calculation returning a number.
- `main.py`: runnable demonstration.
- `test_plugin_loader.py`: exactly 10 unittest tests.

## Plugin contract
Each standalone `.py` module exports:

```python
METADATA = PluginMetadata("unique_name", "1.0", "description")
def initialize(stack): ...  # return state; register resources immediately

def run(state): ...        # return str, int, float, list or dict

def cleanup(): ...         # must also work after partial initialization
```

Import PluginMetadata from `plugin_loader`. Functions must be synchronous;
validation checks metadata, callable members and compatible signatures.
List/dict results must be JSON serializable. Unsupported result types raise
TypeError. singledispatch follows inheritance (e.g. bool uses the int handler).

`PluginLoader.load()` discovers sorted public `.py` files on each call. It imports
and validates them, then creates a LoadedPlugin for each. Accessing its
`cached_property` named `state` initializes it once per session. Calling run
reuses that state. A fresh session creates fresh instances and caches.

ExitStack registers cleanup before initialization. Register resources using
`stack.enter_context(...)` or `stack.callback(...)` immediately after acquiring
them. On success or failure, callbacks run in reverse order: resource cleanup,
plugin cleanup, cached-state invalidation, then removal of the imported module.
Already loaded plugins are also unwound if a later plugin fails. ExitStack
attempts remaining callbacks even when a cleanup callback raises. Exceptions
propagate to the caller; a later load() call can start a new session.

Scope: trusted plugins, synchronous single-threaded sessions, standalone modules
(no relative-import package support). Import-time code and metadata declarations
must not acquire resources: the loader cannot undo arbitrary import side effects.
Cleanup guarantees cover registered resources and cleanup callbacks, not plugins
that leak unregistered resources or whose own cleanup cannot release a resource.

## Tests
1. Discovery filtering and deterministic order.
2. Frozen and validated metadata.
3. Missing interface members, invalid signatures and async functions.
4. Successful execution, resource cleanup and module removal.
5. Initialization cached once per session.
6. Dispatch of supported results and rejection of unknown types.
7. Initialization failure, rollback and successful subsequent session.
8. Cleanup when the context body raises.
9. Import/validation failures roll back previously loaded plugins.
10. Remaining cleanup runs even if a plugin's cleanup raises.
