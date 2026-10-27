"""Synchronous, single-threaded loader for trusted standalone Python plugins."""
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from functools import cached_property, singledispatch
import importlib.util
import inspect
import json
from pathlib import Path
import sys
from types import ModuleType
from uuid import uuid4


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str = ""

    def __post_init__(self):
        for field in ("name", "version", "description"):
            value = getattr(self, field)
            if not isinstance(value, str) or (field != "description" and not value.strip()):
                raise ValueError(f"Invalid metadata field: {field}")


class PluginValidationError(ValueError):
    pass


@singledispatch
def handle_result(result):
    raise TypeError(f"Unsupported result type: {type(result).__name__}")


@handle_result.register(str)
def _(result):
    return f"Text: {result}"


@handle_result.register(int)
@handle_result.register(float)
def _(result):
    return f"Number: {result}"


@handle_result.register(list)
@handle_result.register(dict)
def _(result):
    return json.dumps(result, sort_keys=True)


def discover_plugins(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(folder)
    return sorted(p for p in folder.glob("*.py")
                  if p.is_file() and not p.name.startswith("_"))


def validate_plugin(module):
    if not isinstance(getattr(module, "METADATA", None), PluginMetadata):
        raise PluginValidationError("METADATA must be a PluginMetadata instance")
    # Check call compatibility, not just whether attributes exist.
    for name, args in (("initialize", (object(),)), ("run", (object(),)), ("cleanup", ())):
        function = getattr(module, name, None)
        if (not callable(function) or inspect.iscoroutinefunction(function)
                or inspect.isgeneratorfunction(function)):
            raise PluginValidationError(f"{name} must be a synchronous function")
        try:
            inspect.signature(function).bind(*args)
        except (TypeError, ValueError) as exc:
            raise PluginValidationError(f"Invalid signature for {name}") from exc


class LoadedPlugin:
    def __init__(self, module: ModuleType, stack: ExitStack):
        self.module = module
        self.metadata = module.METADATA
        self._stack = stack
        self._active = True

    @cached_property
    def state(self):
        if not self._active:
            raise RuntimeError("Plugin is closed")
        return self.module.initialize(self._stack)

    def run(self):
        if not self._active:
            raise RuntimeError("Plugin is closed")
        return handle_result(self.module.run(self.state))

    def _deactivate(self):
        self._active = False
        self.__dict__.pop("state", None)


class PluginLoader:
    def __init__(self, folder):
        self.folder = Path(folder)

    @contextmanager
    def load(self):
        """Roll back the entire session on import, validation, init or body failure."""
        with ExitStack() as stack:
            plugins = []
            names = set()
            for path in discover_plugins(self.folder):
                module_name = f"_runtime_plugin_{uuid4().hex}"
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Cannot import {path}")
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                # Registered before execution, so failed imports are removed too.
                stack.callback(sys.modules.pop, module_name, None)
                spec.loader.exec_module(module)
                validate_plugin(module)
                if module.METADATA.name in names:
                    raise PluginValidationError(f"Duplicate plugin: {module.METADATA.name}")
                names.add(module.METADATA.name)
                plugin = LoadedPlugin(module, stack)
                stack.callback(plugin._deactivate)
                # cleanup must support partial initialization.
                stack.callback(module.cleanup)
                plugin.state  # Initialize once; subsequent accesses use the cache.
                plugins.append(plugin)
            yield tuple(plugins)
