"""A small, standard-library-only plugin system for Python 3.9+."""

from __future__ import annotations

import importlib.util
import inspect
import sys
from abc import ABC, abstractmethod
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from functools import cached_property, singledispatch
from pathlib import Path
from typing import Any, ClassVar, Iterator
from uuid import uuid4


class PluginError(Exception):
    """Base exception for plugin loading errors."""


class PluginValidationError(PluginError):
    """A module does not satisfy the plugin interface."""


class PluginLoadError(PluginError):
    """Importing, constructing, or setting up a plugin failed."""


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str = ""

    def __post_init__(self) -> None:
        for field in ("name", "version"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be a non-empty string")
        if not isinstance(self.description, str):
            raise ValueError("description must be a string")


class Plugin(ABC):
    """Plugins must have metadata and implement initialize() and run().

    Constructors and module imports should not acquire resources. Acquire them
    in setup()/initialize(), and release them in cleanup(). Cleanup must also
    tolerate setup failing before initialization has finished.
    """

    metadata: ClassVar[PluginMetadata]

    @cached_property
    def resource(self) -> Any:
        """Compute expensive state once per instance, on its first access."""
        return self.initialize()

    @abstractmethod
    def initialize(self) -> Any:
        """Build the expensive state used by this plugin."""

    def setup(self) -> None:
        """Initialize within the loader's protected context."""
        self.resource

    @abstractmethod
    def run(self) -> Any:
        """Return a result for format_result() to handle."""

    def cleanup(self) -> None:
        """Discard cached state; overrides must release their own resources."""
        self.__dict__.pop("resource", None)


class PluginLoader:
    def __init__(self, folder: Path) -> None:
        self.folder = Path(folder).resolve()

    def discover(self) -> tuple[Path, ...]:
        """Scan again on every call; public, top-level .py files are plugins."""
        if not self.folder.is_dir():
            raise FileNotFoundError(f"Plugin folder does not exist: {self.folder}")
        return tuple(
            sorted(
                path
                for path in self.folder.iterdir()
                if path.is_file()
                and path.suffix == ".py"
                and not path.stem.startswith("_")
            )
        )

    @contextmanager
    def load(self) -> Iterator[tuple[Plugin, ...]]:
        """Load the whole folder, rolling back on any failure.

        ExitStack runs every registered callback, last registered first, even
        if another callback raises. Exceptions are allowed to propagate.
        """
        with ExitStack() as stack:
            plugins = []
            for path in self.discover():
                module = self._import_module(path, stack)
                plugin_class = self._validate_class(module, path)
                try:
                    plugin = plugin_class()
                except Exception as error:
                    raise PluginLoadError(
                        f"{path.name}: plugin construction failed"
                    ) from error

                self._validate_instance(plugin, path)
                # Register FIRST: setup may acquire a resource and then fail.
                stack.callback(plugin.cleanup)
                try:
                    plugin.setup()
                except Exception as error:
                    raise PluginLoadError(
                        f"{path.name}: plugin setup failed"
                    ) from error
                plugins.append(plugin)

            yield tuple(plugins)

    @staticmethod
    def _import_module(path: Path, stack: ExitStack) -> Any:
        # Unique names avoid collisions between folders and repeated loads.
        module_name = f"_homework_plugin_{uuid4().hex}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise PluginLoadError(f"{path.name}: cannot create an import spec")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        # Registered before exec_module, so failed imports are removed too.
        # Plugin cleanup is registered later and runs before module removal.
        stack.callback(sys.modules.pop, module_name, None)
        try:
            spec.loader.exec_module(module)
        except Exception as error:
            raise PluginLoadError(f"{path.name}: plugin import failed") from error
        return module

    @staticmethod
    def _validate_class(module: Any, path: Path) -> type[Plugin]:
        plugin_class = getattr(module, "PLUGIN_CLASS", None)
        if (
            not inspect.isclass(plugin_class)
            or not issubclass(plugin_class, Plugin)
            or inspect.isabstract(plugin_class)
        ):
            raise PluginValidationError(
                f"{path.name}: PLUGIN_CLASS must be a concrete Plugin subclass"
            )
        if not isinstance(getattr(plugin_class, "metadata", None), PluginMetadata):
            raise PluginValidationError(
                f"{path.name}: metadata must be PluginMetadata"
            )
        try:
            inspect.signature(plugin_class).bind()
        except (TypeError, ValueError) as error:
            raise PluginValidationError(
                f"{path.name}: the plugin constructor must accept no arguments"
            ) from error
        return plugin_class

    @staticmethod
    def _validate_instance(plugin: Plugin, path: Path) -> None:
        if not isinstance(getattr(plugin, "metadata", None), PluginMetadata):
            raise PluginValidationError(
                f"{path.name}: metadata must be PluginMetadata"
            )
        for name in ("initialize", "setup", "run", "cleanup"):
            hook = getattr(plugin, name, None)
            if not callable(hook):
                raise PluginValidationError(f"{path.name}: {name} must be callable")
            try:
                inspect.signature(hook).bind()
            except (TypeError, ValueError) as error:
                raise PluginValidationError(
                    f"{path.name}: {name} must accept no arguments"
                ) from error


@singledispatch
def format_result(value: Any) -> str:
    """Dispatch on the result's type; unsupported types fail explicitly."""
    raise TypeError(f"Unsupported plugin result type: {type(value).__name__}")


@format_result.register(str)
def _format_text(value: str) -> str:
    return f"Text: {value}"


@format_result.register(int)
def _format_integer(value: int) -> str:
    return f"Integer: {value}"


@format_result.register(float)
def _format_float(value: float) -> str:
    return f"Float: {value:g}"


@format_result.register(bool)
def _format_boolean(value: bool) -> str:
    # bool is a subclass of int, so give it its own, more specific handler.
    return f"Boolean: {str(value).lower()}"


@format_result.register(type(None))
def _format_none(value: None) -> str:
    return "No result"


@format_result.register(list)
def _format_list(value: list) -> str:
    return "List: [" + ", ".join(format_result(item) for item in value) + "]"


@format_result.register(dict)
def _format_mapping(value: dict) -> str:
    entries = (f"{key!r}: {format_result(item)}" for key, item in value.items())
    return "Mapping: {" + ", ".join(entries) + "}"
