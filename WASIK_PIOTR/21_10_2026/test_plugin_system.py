import pytest
from pathlib import Path
from typing import Any
from plugin_system import (
    PluginMetadata,
    PluginInterface,
    BasePlugin,
    PluginLoaderContext,
    PluginManager,
    TextResult,
    NumericResult,
    handle_result,
)


# Pomocnicza poprawna wtyczka do testów
class DummyValidPlugin(BasePlugin):
    def __init__(self):
        super().__init__(PluginMetadata("DummyPlugin", "1.0.0", "Tester"))
        self.is_initialized = False
        self.is_cleaned_up = False

    def initialize(self) -> None:
        self.is_initialized = True

    def run(self) -> TextResult:
        return TextResult(f"Heavy resource state: {self.heavy_resource['status']}")

    def cleanup(self) -> None:
        self.is_cleaned_up = True


# Pomocnicza wtyczka rzucająca błąd podczas inicjalizacji
class FailingPlugin(BasePlugin):
    def __init__(self):
        super().__init__(PluginMetadata("FailingPlugin", "0.1", "Tester"))
        self.cleaned_up_after_failure = False

    def initialize(self) -> None:
        raise RuntimeError("Initialization crashed!")

    def run(self) -> Any:
        return None

    def cleanup(self) -> None:
        self.cleaned_up_after_failure = True


# --- 10 TESTÓW ---

def test_metadata_is_frozen():
    """1. Testuje czy PluginMetadata jest immutowalne (frozen)."""
    meta = PluginMetadata("Test", "1.0", "Author")
    with pytest.raises(AttributeError):
        meta.name = "NewName"


def test_interface_validation():
    """2. Sprawdza poprawność walidacji interfejsu (Protocol)."""
    plugin = DummyValidPlugin()
    assert isinstance(plugin, PluginInterface)


def test_singledispatch_text_result():
    """3. Sprawdza działanie singledispatch dla TextResult."""
    res = TextResult("hello world")
    assert handle_result(res) == "[TEXT PLUGIN OUTPUT]: HELLO WORLD"


def test_singledispatch_numeric_result():
    """4. Sprawdza działanie singledispatch dla NumericResult."""
    res = NumericResult(21.0)
    assert handle_result(res) == "[NUMERIC PLUGIN OUTPUT]: 42.00"


def test_singledispatch_fallback():
    """5. Sprawdza obsługę domyślną singledispatch."""
    assert handle_result("raw string") == "Processed unknown result type: raw string"


def test_cached_property_caching():
    """6. Upewnia się, że cached_property oblicza wartość tylko raz."""
    plugin = DummyValidPlugin()
    res1 = plugin.heavy_resource
    res2 = plugin.heavy_resource
    assert res1 is res2


def test_context_manager_normal_flow():
    """7. Sprawdza czy context manager inicjalizuje i sprząta w normalnym cyklu."""
    plugin = DummyValidPlugin()
    with PluginLoaderContext(plugin) as loaded:
        assert loaded.is_initialized is True
        assert loaded.is_cleaned_up is False
    assert plugin.is_cleaned_up is True


def test_context_manager_recovers_on_exception():
    """8. KLUCZOWY TEST: Wtyczka rzuca wyjątek podczas ładowania, a CM sprząta zasoby."""
    failing_plugin = FailingPlugin()
    
    with pytest.raises(RuntimeError, match="Initialization crashed!"):
        with PluginLoaderContext(failing_plugin):
            pass

    # Gwarancja, że cleanup został wywołany pomimo awarii inicjalizacji
    assert failing_plugin.cleaned_up_after_failure is True


def test_plugin_manager_empty_dir(tmp_path: Path):
    """9. Sprawdza zachowanie PluginManagera w pustym katalogu."""
    manager = PluginManager(tmp_path)
    loaded = manager.discover_and_load()
    assert len(loaded) == 0


def test_plugin_manager_discovers_and_loads(tmp_path: Path):
    """10. Dynamicznie tworzy plik wtyczki i sprawdza jej automatyczne odkrywanie."""
    plugin_code = """
from plugin_system import BasePlugin, PluginMetadata, TextResult

class DynamicPlugin(BasePlugin):
    def __init__(self):
        super().__init__(PluginMetadata("Dynamic", "1.0", "Auto"))
    def initialize(self):
        pass
    def run(self):
        return TextResult("dynamic execution")
    def cleanup(self):
        pass
"""
    plugin_file = tmp_path / "dynamic_plugin.py"
    plugin_file.write_text(plugin_code)

    manager = PluginManager(tmp_path)
    loaded = manager.discover_and_load()
    
    assert "Dynamic" in loaded
    assert loaded["Dynamic"].run().text == "dynamic execution"