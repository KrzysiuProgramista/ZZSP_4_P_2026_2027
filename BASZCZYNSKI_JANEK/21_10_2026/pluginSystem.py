"""
Advanced Python - Module 4 Challenge: Resilient Plugin Loader System.

Combines:
- Resource management via Context Managers & ExitStack
- Strict data contracts using Frozen Dataclasses
- Functional composition using singledispatch and cached_property
"""

from __future__ import annotations

import sys
import importlib.util
from contextlib import ExitStack, contextmanager
from dataclasses import dataclass
from functools import cached_property, singledispatch
from pathlib import Path
from typing import Any, Callable, Generator, Protocol, runtime_checkable


# ============================================================================
# 1. DATA MODEL (Frozen Dataclass)
# ============================================================================

@dataclass(frozen=True, slots=True)
class PluginMetadata:
    """Immutable plugin metadata contract."""
    name: str
    version: str
    capabilities: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name or not isinstance(self.name, str):
            raise ValueError("Plugin metadata 'name' must be a non-empty string.")
        if not self.version or not isinstance(self.version, str):
            raise ValueError("Plugin metadata 'version' must be a non-empty string.")


# ============================================================================
# 2. INTERFACE DEFINITION & BASE PROTOCOL
# ============================================================================

class PluginError(Exception):
    """Base exception for plugin loader failures."""


class PluginValidationError(PluginError):
    """Raised when a plugin fails interface validation."""


class PluginLoadError(PluginError):
    """Raised when a plugin fails during acquisition or initialization."""


@runtime_checkable
class PluginInterface(Protocol):
    """Structural interface contract that every valid plugin must satisfy."""
    metadata: PluginMetadata
    cleaned_up: bool

    def execute(self, *args: Any, **kwargs: Any) -> Any: ...
    def cleanup(self) -> None: ...


class BasePlugin:
    """
    Standard base implementation with cached expensive initialisation.
    Subclasses must set `metadata` and implement `_setup_resource` & `execute`.
    """
    metadata: PluginMetadata
    init_count: int = 0
    cleaned_up: bool = False

    def _setup_resource(self) -> Any:
        """Simulates expensive setup (e.g., loading model weights, connection pool)."""
        return {"status": "ready"}

    @cached_property
    def resource(self) -> Any:
        """
        Caches costly setup once per instance.
        If initialisation fails, the error propagates before publication.
        """
        self.init_count += 1
        return self._setup_resource()

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def cleanup(self) -> None:
        """Teardown logic to release acquired state."""
        self.cleaned_up = True


# ============================================================================
# 3. RESULT HANDLER (singledispatch)
# ============================================================================

@singledispatch
def dispatch_plugin_result(result: Any) -> str:
    """Default fallback handler for unknown plugin result types."""
    return f"Generic result [{type(result).__name__}]: {result!r}"


@dispatch_plugin_result.register
def _(result: int) -> str:
    return f"Metric counter: {result:,}"


@dispatch_plugin_result.register
def _(result: str) -> str:
    return f"Text payload: {result.strip()}"


@dispatch_plugin_result.register
def _(result: dict) -> str:
    keys = ", ".join(sorted(str(k) for k in result.keys()))
    return f"Structured record with keys: [{keys}]"


@dispatch_plugin_result.register
def _(result: list) -> str:
    return f"Collection with {len(result)} items"


# ============================================================================
# 4. DISCOVERY & VALIDATION
# ============================================================================

def discover_plugin_modules(directory: Path | str) -> list[Path]:
    """
    Scans a folder for valid plugin source files (.py),
    ignoring private/dunder files, sorted deterministically.
    """
    target = Path(directory)
    if not target.is_dir():
        raise FileNotFoundError(f"Directory not found: {target}")

    candidates = [
        path for path in target.iterdir()
        if path.is_file()
        and path.suffix == ".py"
        and not path.name.startswith(("_", "."))
    ]
    return sorted(candidates, key=lambda p: p.stem)


def validate_plugin_instance(plugin: Any) -> None:
    """Verifies that an instantiated object meets the PluginInterface specification."""
    if not isinstance(plugin, PluginInterface):
        missing = [
            attr for attr in ("metadata", "execute", "cleanup")
            if not hasattr(plugin, attr)
        ]
        raise PluginValidationError(
            f"Plugin {type(plugin).__name__} missing required attributes: {missing}"
        )
    if not isinstance(plugin.metadata, PluginMetadata):
        raise PluginValidationError(
            f"Plugin {type(plugin).__name__} 'metadata' must be a PluginMetadata instance."
        )


def _load_plugin_module(path: Path) -> Any:
    """Dynamically imports a module from a filesystem path."""
    module_name = f"dynamic_plugin_{path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise PluginLoadError(f"Could not load module specification from {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(module_name, None)
        raise
    return module


# ============================================================================
# 5. CONTEXT MANAGER (Safe Loader with ExitStack)
# ============================================================================

@contextmanager
def load_plugins(
    directory: Path | str,
    trigger_warmup: bool = True,
) -> Generator[list[PluginInterface], None, None]:
    """
    Discovers, validates, and initialises plugins within a managed scope.

    Lifecycle guarantees:
    - If any plugin fails during discovery, instantiation, or cached setup,
      ALL earlier loaded plugins are immediately cleaned up.
    - Upon normal exit from the 'with' block, all loaded plugins are cleaned up.
    - Upon unexpected exception inside the 'with' block, cleanup still occurs.
    """
    plugin_files = discover_plugin_modules(directory)
    loaded: list[PluginInterface] = []

    with ExitStack() as cleanup_stack:
        for file_path in plugin_files:
            module = _load_plugin_module(file_path)

            plugin_factory: Callable[[], Any] | None = getattr(module, "get_plugin", None)
            if plugin_factory is None:
                plugin_cls = getattr(module, "Plugin", None)
                if plugin_cls is None:
                    raise PluginValidationError(
                        f"Module {file_path.name} must export 'Plugin' class or 'get_plugin()' factory."
                    )
                plugin_factory = plugin_cls

            try:
                instance = plugin_factory()
            except Exception as exc:
                raise PluginLoadError(
                    f"Instantiation failed for {file_path.name}: {exc}"
                ) from exc

            # Validate interface contract
            validate_plugin_instance(instance)

            # Register cleanup callback immediately into the stack
            cleanup_stack.callback(instance.cleanup)

# Warm up / verify cached initialization if requested
            if trigger_warmup and hasattr(type(instance), "resource"):
                try:
                    _ = instance.resource
                except Exception as exc:
                    raise PluginLoadError(
                        f"Resource warm-up failed for {instance.metadata.name}: {exc}"
                    ) from exc

            loaded.append(instance)

        # Hand over control to the consumer
        yield loaded

    # On exiting the with-block (normally or via exception), cleanup_stack runs all callbacks in LIFO order