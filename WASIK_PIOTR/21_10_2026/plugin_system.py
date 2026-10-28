import abc
import importlib.util
import sys
from dataclasses import dataclass
from functools import cached_property, singledispatch
from pathlib import Path
from typing import Any, Dict, Protocol, Type, runtime_checkable


# 1. Metadane wtyczki jako frozen dataclass
@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    author: str


# Types for plugin outputs handled by singledispatch
@dataclass(frozen=True)
class TextResult:
    text: str


@dataclass(frozen=True)
class NumericResult:
    value: float


# 2. Interfejs wtyczki (Protocol)
@runtime_checkable
class PluginInterface(Protocol):
    metadata: PluginMetadata

    def initialize(self) -> None:
        ...

    def run(self) -> Any:
        ...

    def cleanup(self) -> None:
        ...


# 3. Handling różnych typów wyników z wtyczek przez singledispatch
@singledispatch
def handle_result(result: Any) -> str:
    """Domyślny handler dla nieobsługiwanych typów wyników."""
    return f"Processed unknown result type: {result}"


@handle_result.register
def _(result: TextResult) -> str:
    return f"[TEXT PLUGIN OUTPUT]: {result.text.upper()}"


@handle_result.register
def _(result: NumericResult) -> str:
    return f"[NUMERIC PLUGIN OUTPUT]: {result.value * 2:.2f}"


# 4. Ładowanie wtyczki z użyciem Context Managera (Gwarancja sprzątania przy błędzie)
class PluginLoaderContext:
    def __init__(self, plugin_instance: PluginInterface):
        self.plugin = plugin_instance
        self.initialized_successfully = False

    def __enter__(self) -> PluginInterface:
        try:
            self.plugin.initialize()
            self.initialized_successfully = True
            return self.plugin
        except Exception as err:
            # Gdy inicjalizacja się nie powiedzie, sprzątamy przed przepuszczeniem wyjątku
            self.plugin.cleanup()
            raise err

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Sprzątanie po zakończeniu bloku with
        if self.initialized_successfully:
            self.plugin.cleanup()
        # Zwraca False / None -> wyjątki nie są ukrywane
        return False


# 5. Klasa Wtyczki z cached_property
class BasePlugin(abc.ABC):
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata

    @cached_property
    def heavy_resource(self) -> Dict[str, Any]:
        """Kosztowna operacja inicjalizacyjna cachowana przez cached_property."""
        # Udawanie kosztownego pobierania danych / ładowania modelu
        return {"loaded_data": list(range(1000)), "status": "ready"}

    @abc.abstractmethod
    def initialize(self) -> None:
        pass

    @abc.abstractmethod
    def run(self) -> Any:
        pass

    @abc.abstractmethod
    def cleanup(self) -> None:
        pass


class PluginManager:
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.loaded_plugins: Dict[str, PluginInterface] = {}

    def discover_and_load(self) -> Dict[str, PluginInterface]:
        """Odkrywa moduły .py w podanym katalogu, waliduje i bezpiecznie je ładuje."""
        if not self.plugin_dir.exists():
            return self.loaded_plugins

        for file_path in self.plugin_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue

            module_name = file_path.stem
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)
            except Exception:
                continue

            # Szukamy atrybutu/klasy spełniającej PluginInterface
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    try:
                        instance = attr()
                        if isinstance(instance, PluginInterface):
                            # Ładujemy przez Context Manager
                            with PluginLoaderContext(instance) as loaded_plugin:
                                self.loaded_plugins[loaded_plugin.metadata.name] = loaded_plugin
                    except Exception as e:
                        print(f"Failed to safely load plugin from {file_path.name}: {e}")

        return self.loaded_plugins