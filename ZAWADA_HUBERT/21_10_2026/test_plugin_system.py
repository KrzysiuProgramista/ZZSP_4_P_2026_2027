import pytest
import pathlib
from plugin_system import PluginMetadata, PluginInterface, PluginContext, PluginLoader, process_result

def test_metadata_frozen():
    meta = PluginMetadata("test", "1.0")
    with pytest.raises(Exception):
        meta.version = "2.0"

def test_singledispatch_int():
    assert process_result(5) == 15

def test_singledispatch_str():
    assert process_result("hello") == "HELLO"

def test_singledispatch_default():
    assert process_result([1, 2]) == "[1, 2]"

def test_cached_property():
    class Dummy:
        def __init__(self):
            self.counter = 0
        @cached_property
        def val(self):
            self.counter += 1
            return 42
    d = Dummy()
    assert d.val == 42
    assert d.counter == 1
    assert d.val == 42
    assert d.counter == 1

class GoodPlugin(PluginInterface):
    metadata = PluginMetadata("good", "1.0")
    def __init__(self):
        self.initialized = False
    def initialize(self):
        self.initialized = True
    def cleanup(self):
        self.initialized = False
    def run(self):
        return 100

class BadPlugin(PluginInterface):
    metadata = PluginMetadata("bad", "1.0")
    def initialize(self):
        raise RuntimeError("fail")
    def run(self):
        return 0

class CleanupTrackedPlugin(PluginInterface):
    metadata = PluginMetadata("tracked", "1.0")
    def __init__(self):
        self.cleaned = False
    def cleanup(self):
        self.cleaned = True
    def run(self):
        return 1

def test_context_manager_success():
    p = GoodPlugin()
    with PluginContext([p]):
        assert p.initialized is True
    assert p.initialized is False

def test_context_manager_recovery():
    p1 = CleanupTrackedPlugin()
    p2 = BadPlugin()
    with pytest.raises(RuntimeError):
        with PluginContext([p1, p2]):
            pass
    assert p1.cleaned is True

def test_plugin_loader(tmp_path):
    plugin_code = """
from plugin_system import PluginInterface, PluginMetadata
class DynamicPlugin(PluginInterface):
    metadata = PluginMetadata("dynamic", "1.0")
    def run(self):
        return "dynamic"
"""
    p_file = tmp_path / "my_plugin.py"
    p_file.write_text(plugin_code)
    loader = PluginLoader()
    plugins = loader.load_from_folder(tmp_path)
    assert len(plugins) == 1
    assert plugins[0].run() == "dynamic"

def test_plugin_interface():
    p = GoodPlugin()
    assert isinstance(p, PluginInterface)
    assert p.metadata.name == "good"

def test_plugin_run():
    p = GoodPlugin()
    assert p.run() == 100