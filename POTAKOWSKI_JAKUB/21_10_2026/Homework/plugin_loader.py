"""Runtime discovery and lifecycle management for Python plugins."""

from __future__ import annotations

import importlib.util
import sys
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from functools import cached_property, singledispatch
from pathlib import Path
from types import ModuleType
from typing import Callable, Iterator, Protocol
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class PluginMetadata:
    name: str
    version: str
    description: str = ""


class Plugin(Protocol):
    metadata: PluginMetadata

    def initialize(self) -> None: ...

    def process(self, value: object) -> object: ...

    def close(self) -> None: ...


class PluginLoadError(RuntimeError):
    """Raised when a discovered module does not satisfy the plugin contract."""


def discover_plugins(directory: str | Path) -> list[Path]:
    """Return Python plugin modules in a directory, in deterministic order."""
    plugin_dir = Path(directory)
    if not plugin_dir.is_dir():
        raise NotADirectoryError(f"Plugin directory does not exist: {plugin_dir}")

    return sorted(
        path
        for path in plugin_dir.glob("*.py")
        if not path.name.startswith("_")
    )


def validate_plugin(plugin: object) -> None:
    """Raise PluginLoadError unless an object implements the plugin contract."""
    if not isinstance(getattr(plugin, "metadata", None), PluginMetadata):
        raise PluginLoadError("Plugin must provide PluginMetadata as metadata")

    missing = [
        method
        for method in ("initialize", "process", "close")
        if not callable(getattr(plugin, method, None))
    ]
    if missing:
        raise PluginLoadError(
            "Plugin is missing required callable(s): " + ", ".join(missing)
        )


class PluginContext:
    """Initialize a plugin once and close it when its context exits."""

    def __init__(self, factory: Callable[[], Plugin]) -> None:
        self._factory = factory

    @cached_property
    def plugin(self) -> Plugin:
        plugin = self._factory()
        validate_plugin(plugin)
        try:
            plugin.initialize()
        except BaseException:
            plugin.close()
            raise
        return plugin

    def __enter__(self) -> Plugin:
        return self.plugin

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> bool:
        if "plugin" in self.__dict__:
            self.plugin.close()
        return False


class PluginLoader:
    """Discover and manage plugins from a directory of Python modules.

    Each module must expose a callable ``create_plugin()`` factory.
    """

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    @contextmanager
    def load_plugins(self) -> Iterator[list[Plugin]]:
        loaded: list[Plugin] = []
        with ExitStack() as stack:
            for path in discover_plugins(self.directory):
                module_name = f"_runtime_plugin_{path.stem}_{uuid4().hex}"
                try:
                    module = self._import_module(path, module_name)
                    factory = getattr(module, "create_plugin", None)
                    if not callable(factory):
                        raise PluginLoadError(
                            f"{path.name} must define a callable create_plugin()"
                        )
                    loaded.append(stack.enter_context(PluginContext(factory)))
                finally:
                    sys.modules.pop(module_name, None)
            yield loaded

    @staticmethod
    def _import_module(path: Path, module_name: str) -> ModuleType:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"Cannot load plugin module: {path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:
            sys.modules.pop(module_name, None)
            raise
        return module


@singledispatch
def handle_result(result: object) -> str:
    """Convert a plugin result to displayable text."""
    return repr(result)


@handle_result.register
def _(result: str) -> str:
    return result


@handle_result.register
def _(result: int) -> str:
    return str(result)


@handle_result.register
def _(result: list) -> str:
    return ", ".join(str(item) for item in result)


@handle_result.register
def _(result: dict) -> str:
    import json

    return json.dumps(result, sort_keys=True)
