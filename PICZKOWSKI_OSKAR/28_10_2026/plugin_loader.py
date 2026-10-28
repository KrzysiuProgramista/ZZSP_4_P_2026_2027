"""Runtime plugin discovery, validation, cleanup, and result dispatch."""
from contextlib import contextmanager
from dataclasses import dataclass
from functools import cached_property, singledispatch
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str


@dataclass
class LoadedPlugin:
    metadata: PluginMetadata
    instance: Any

    @cached_property
    def expensive_initialisation(self):
        """Stand-in for expensive setup; cached after its first access."""
        return {"plugin": self.metadata.name, "ready": True}


def handle_result(result):
    """Convert supported plugin result types to user-friendly text."""
    return _handle_result(result)


@singledispatch
def _handle_result(result):
    return f"Unsupported result type: {type(result).__name__}"


@_handle_result.register
def _(result: str):
    return result


@_handle_result.register
def _(result: int):
    return f"Integer result: {result}"


@_handle_result.register
def _(result: list):
    return f"List result with {len(result)} item(s)"


@_handle_result.register
def _(result: dict):
    return f"Dictionary result with keys: {', '.join(map(str, result.keys()))}"


def _load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(f"loaded_plugin_{path.stem}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_module(module: ModuleType) -> PluginMetadata:
    metadata = getattr(module, "METADATA", None)
    if not isinstance(metadata, PluginMetadata):
        # Accept equivalent frozen dataclasses declared by plugin modules.
        if not (metadata is not None and getattr(type(metadata), "__dataclass_params__", None)
                and type(metadata).__dataclass_params__.frozen
                and all(hasattr(metadata, field) for field in ("name", "version", "description"))):
            raise TypeError("Plugin must define frozen dataclass METADATA")
    if not callable(getattr(module, "load", None)):
        raise TypeError("Plugin must provide callable load()")
    return PluginMetadata(metadata.name, metadata.version, metadata.description)


def discover_plugins(folder):
    """Discover Python modules in folder, excluding __init__.py."""
    folder = Path(folder)
    return sorted(path for path in folder.glob("*.py") if path.name != "__init__.py")


@contextmanager
def loaded_plugins(folder):
    """Load plugins; close already-loaded instances if loading later fails."""
    loaded = []
    try:
        for path in discover_plugins(folder):
            module = _load_module(path)
            metadata = _validate_module(module)
            instance = module.load()
            if not callable(getattr(instance, "run", None)):
                close = getattr(instance, "close", None)
                if callable(close):
                    close()
                raise TypeError(f"Plugin {metadata.name!r} must implement run(value)")
            loaded.append(LoadedPlugin(metadata, instance))
        yield loaded
    finally:
        for plugin in reversed(loaded):
            close = getattr(plugin.instance, "close", None)
            if callable(close):
                close()
