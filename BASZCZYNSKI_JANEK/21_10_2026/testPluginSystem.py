"""
Test suite covering discovery, interface enforcement, cached initialisation,
exception dispatching, and resource lifecycle guarantees.
"""

from pathlib import Path
import pytest

from pluginSystem import (
    BasePlugin,
    PluginInterface,
    PluginLoadError,
    PluginMetadata,
    PluginValidationError,
    discover_plugin_modules,
    dispatch_plugin_result,
    load_plugins,
)


# ----------------------------------------------------------------------------
# Test Fixtures & Helpers
# ----------------------------------------------------------------------------

def write_plugin_file(directory: Path, filename: str, content: str) -> Path:
    target = directory / filename
    target.write_text(content, encoding="utf-8")
    return target


# ----------------------------------------------------------------------------
# 1. DISCOVERY & FILTERING TESTS
# ----------------------------------------------------------------------------

def test_discover_valid_plugins(tmp_path: Path):
    """Test 1: Discovers valid .py files in a folder."""
    write_plugin_file(tmp_path, "plugin_b.py", "# valid")
    write_plugin_file(tmp_path, "plugin_a.py", "# valid")

    discovered = discover_plugin_modules(tmp_path)
    assert len(discovered) == 2
    assert [p.name for p in discovered] == ["plugin_a.py", "plugin_b.py"]


def test_ignores_unrelated_files(tmp_path: Path):
    """Test 2: Ignores non-.py files and hidden/dunder files."""
    write_plugin_file(tmp_path, "valid.py", "# valid")
    write_plugin_file(tmp_path, "__init__.py", "# package file")
    write_plugin_file(tmp_path, "_private.py", "# private file")
    write_plugin_file(tmp_path, "notes.txt", "some docs")
    write_plugin_file(tmp_path, "config.json", "{}")

    discovered = discover_plugin_modules(tmp_path)
    assert len(discovered) == 1
    assert discovered[0].name == "valid.py"


def test_deterministic_order(tmp_path: Path):
    """Test 3: Plugins are discovered in deterministic alphabetical order."""
    names = ["zeta.py", "alpha.py", "gamma.py", "beta.py"]
    for n in names:
        write_plugin_file(tmp_path, n, "# dummy")

    discovered = discover_plugin_modules(tmp_path)
    assert [p.stem for p in discovered] == ["alpha", "beta", "gamma", "zeta"]


# ----------------------------------------------------------------------------
# 2. CONTRACT & METADATA VALIDATION TESTS
# ----------------------------------------------------------------------------

def test_rejects_missing_required_interface(tmp_path: Path):
    """Test 4: Rejects module missing execute() or required methods."""
    bad_code = """
from pluginSystem import PluginMetadata

class Plugin:
    metadata = PluginMetadata(name="Incomplete", version="1.0")
    cleaned_up = False
    # Missing execute() and cleanup()
"""
    write_plugin_file(tmp_path, "incomplete.py", bad_code)

    with pytest.raises(PluginValidationError, match="missing required attributes"):
        with load_plugins(tmp_path):
            pass


def test_rejects_invalid_metadata(tmp_path: Path):
    """Test 5: Rejects plugin with invalid or non-frozen metadata."""
    bad_code = """
class Plugin:
    metadata = "invalid_string_metadata"
    cleaned_up = False
    def execute(self): return 1
    def cleanup(self): self.cleaned_up = True
"""
    write_plugin_file(tmp_path, "invalid_meta.py", bad_code)

    with pytest.raises(PluginValidationError, match="must be a PluginMetadata instance"):
        with load_plugins(tmp_path):
            pass


def test_frozen_metadata_immutability():
    """Test 6: Proves metadata is frozen and cannot be mutated at runtime."""
    meta = PluginMetadata(name="Analyzer", version="2.1.0", capabilities=("read", "write"))
    with pytest.raises(AttributeError):
        meta.version = "2.2.0"  # type: ignore


# ----------------------------------------------------------------------------
# 3. LIFECYCLE, CACHING & CLEANUP RECOVERY TESTS
# ----------------------------------------------------------------------------

def test_cached_initialization_once_per_instance():
    """Test 7: Cached property runs heavy setup exactly once per instance."""
    class DummyPlugin(BasePlugin):
        metadata = PluginMetadata("Dummy", "1.0")
        def __init__(self):
            super().__init__()
            self.expensive_calls = 0

        def _setup_resource(self):
            self.expensive_calls += 1
            return "heavy_connection"

        def execute(self):
            return self.resource

    plugin = DummyPlugin()
    assert plugin.expensive_calls == 0

    # Access property multiple times
    _ = plugin.resource
    _ = plugin.resource
    res = plugin.execute()

    assert res == "heavy_connection"
    assert plugin.expensive_calls == 1  # Computed only once!


def test_cleanup_on_normal_exit(tmp_path: Path):
    """Test 8: Normal exit cleans up every loaded plugin."""
    code = """
from pluginSystem import BasePlugin, PluginMetadata

class Plugin(BasePlugin):
    metadata = PluginMetadata(name="Healthy", version="1.0")
    def execute(self): return "ok"
"""
    write_plugin_file(tmp_path, "healthy.py", code)

    loaded_ref = None
    with load_plugins(tmp_path) as plugins:
        assert len(plugins) == 1
        loaded_ref = plugins[0]
        assert loaded_ref.cleaned_up is False

    assert loaded_ref.cleaned_up is True


def test_failure_during_loading_cleans_up_earlier_resources(tmp_path: Path):
    """
    Test 9 (CRUCIAL): When plugin 2 raises during loading/warm-up,
    earlier loaded plugin 1 MUST be cleaned up before the exception escapes.
    """
    plugin_1_code = """
from pluginSystem import BasePlugin, PluginMetadata

class Plugin(BasePlugin):
    metadata = PluginMetadata(name="FirstValid", version="1.0")
    cleaned_instances = []

    def execute(self):
        return "first_ok"

    def cleanup(self):
        super().cleanup()
        Plugin.cleaned_instances.append(self)
"""
    # Plugin 2 raises an exception during cached property warm-up
    plugin_2_code = """
from pluginSystem import BasePlugin, PluginMetadata

class Plugin(BasePlugin):
    metadata = PluginMetadata(name="FailingSecond", version="1.0")

    def _setup_resource(self):
        raise RuntimeError("Crash during plugin 2 resource allocation!")

    def execute(self):
        return 0
"""
    write_plugin_file(tmp_path, "01_first.py", plugin_1_code)
    write_plugin_file(tmp_path, "02_second.py", plugin_2_code)

    # Triggering load must raise PluginLoadError, and 01_first MUST be cleaned up
    with pytest.raises(PluginLoadError, match="Crash during plugin 2"):
        with load_plugins(tmp_path, trigger_warmup=True):
            pass

    # Verify via the imported module that FirstValid's cleanup was called!
    import sys
    first_mod = sys.modules["dynamic_plugin_01_first"]
    first_cls = getattr(first_mod, "Plugin")
    assert len(first_cls.cleaned_instances) == 1
    assert first_cls.cleaned_instances[0].cleaned_up is True


def test_cleanup_occurs_after_body_execution_failure(tmp_path: Path):
    """Test 10: Cleanup still occurs even if the consumer raises inside the with-block."""
    code = """
from pluginSystem import BasePlugin, PluginMetadata

class Plugin(BasePlugin):
    metadata = PluginMetadata(name="BodyFailTest", version="1.0")
    def execute(self): return 42
"""
    write_plugin_file(tmp_path, "runner.py", code)

    captured_plugin = None
    with pytest.raises(ZeroDivisionError):
        with load_plugins(tmp_path) as plugins:
            captured_plugin = plugins[0]
            _ = 1 / 0  # Interrupt the with-body

    assert captured_plugin is not None
    assert captured_plugin.cleaned_up is True


# ----------------------------------------------------------------------------
# 4. SINGLEDISPATCH TESTS
# ----------------------------------------------------------------------------

def test_singledispatch_result_formatting():
    """Test 11: singledispatch correctly formats int, str, dict, list, and unhandled objects."""
    assert dispatch_plugin_result(10_000) == "Metric counter: 10,000"
    assert dispatch_plugin_result("  hello world  ") == "Text payload: hello world"
    assert dispatch_plugin_result({"status": 200, "latency": 15}) == "Structured record with keys: [latency, status]"
    assert dispatch_plugin_result([1, 2, 3]) == "Collection with 3 items"

    # Default fallback
    assert dispatch_plugin_result(3.1415) == "Generic result [float]: 3.1415"