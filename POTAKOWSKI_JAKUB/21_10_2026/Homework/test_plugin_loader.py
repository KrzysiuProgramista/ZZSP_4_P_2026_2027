import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

from plugin_loader import (
    PluginContext,
    PluginLoadError,
    PluginLoader,
    PluginMetadata,
    discover_plugins,
    handle_result,
    validate_plugin,
)


class ExamplePlugin:
    metadata = PluginMetadata("example", "1.0")

    def __init__(self):
        self.initialized = 0
        self.closed = 0

    def initialize(self):
        self.initialized += 1

    def process(self, value):
        return value

    def close(self):
        self.closed += 1


class PluginLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.plugin_dir = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_plugin(self, name, source):
        path = self.plugin_dir / name
        path.write_text(source, encoding="utf-8")
        return path

    def test_discovers_python_modules_in_sorted_order(self):
        self.write_plugin("zeta.py", "")
        self.write_plugin("alpha.py", "")
        self.write_plugin("_helper.py", "")
        (self.plugin_dir / "notes.txt").write_text("not a plugin", encoding="utf-8")

        self.assertEqual(
            [path.name for path in discover_plugins(self.plugin_dir)],
            ["alpha.py", "zeta.py"],
        )

    def test_discovery_rejects_missing_directory(self):
        missing = self.plugin_dir / "missing"

        with self.assertRaises(NotADirectoryError):
            discover_plugins(missing)

    def test_plugin_metadata_is_frozen(self):
        metadata = PluginMetadata("sample", "1.0")

        with self.assertRaises(FrozenInstanceError):
            metadata.name = "changed"

    def test_valid_plugin_satisfies_interface(self):
        validate_plugin(ExamplePlugin())

    def test_invalid_plugin_reports_missing_interface_methods(self):
        class IncompletePlugin:
            metadata = PluginMetadata("incomplete", "1.0")

        with self.assertRaisesRegex(PluginLoadError, "initialize, process, close"):
            validate_plugin(IncompletePlugin())

    def test_result_dispatch_handles_strings_and_integers(self):
        self.assertEqual(handle_result("ready"), "ready")
        self.assertEqual(handle_result(42), "42")

    def test_result_dispatch_handles_lists_and_dictionaries(self):
        self.assertEqual(handle_result(["a", 2]), "a, 2")
        self.assertEqual(handle_result({"b": 2, "a": 1}), '{"a": 1, "b": 2}')

    def test_loader_initializes_yields_and_closes_plugin(self):
        self.write_plugin(
            "sample.py",
            """
from plugin_loader import PluginMetadata

class Sample:
    metadata = PluginMetadata("sample", "1.0")
    initialized = False
    closed = False

    def initialize(self):
        self.initialized = True

    def process(self, value):
        return value

    def close(self):
        self.closed = True

def create_plugin():
    return Sample()
""",
        )
        loader = PluginLoader(self.plugin_dir)

        with loader.load_plugins() as plugins:
            self.assertEqual(len(plugins), 1)
            plugin = plugins[0]
            self.assertTrue(plugin.initialized)
            self.assertEqual(plugin.process("input"), "input")

        self.assertTrue(plugin.closed)

    def test_cached_property_initializes_plugin_only_once(self):
        plugin = ExamplePlugin()
        context = PluginContext(lambda: plugin)

        with context as first:
            second = context.plugin
            self.assertIs(first, second)
            self.assertEqual(plugin.initialized, 1)

        self.assertEqual(plugin.closed, 1)

    def test_failed_load_cleans_up_and_loader_recovers(self):
        events = self.plugin_dir / "events.txt"
        marker = repr(str(events))
        self.write_plugin(
            "a_good.py",
            f"""
from pathlib import Path
from plugin_loader import PluginMetadata

class Good:
    metadata = PluginMetadata("good", "1.0")
    def initialize(self): pass
    def process(self, value): return value
    def close(self):
        with Path({marker}).open("a", encoding="utf-8") as file:
            file.write("good-close\\n")

def create_plugin(): return Good()
""",
        )
        failing_path = self.write_plugin(
            "b_failing.py",
            f"""
from pathlib import Path
from plugin_loader import PluginMetadata

class Failing:
    metadata = PluginMetadata("failing", "1.0")
    def initialize(self): raise RuntimeError("initialization failed")
    def process(self, value): return value
    def close(self):
        with Path({marker}).open("a", encoding="utf-8") as file:
            file.write("failing-close\\n")

def create_plugin(): return Failing()
""",
        )
        loader = PluginLoader(self.plugin_dir)

        with self.assertRaisesRegex(RuntimeError, "initialization failed"):
            with loader.load_plugins():
                self.fail("A failed plugin must not be yielded")

        self.assertEqual(
            events.read_text(encoding="utf-8").splitlines(),
            ["failing-close", "good-close"],
        )

        failing_path.write_text(
            """
from plugin_loader import PluginMetadata

class Recovered:
    metadata = PluginMetadata("recovered", "1.0")
    def initialize(self): pass
    def process(self, value): return value
    def close(self): pass

def create_plugin(): return Recovered()
""",
            encoding="utf-8",
        )
        with loader.load_plugins() as plugins:
            self.assertEqual(
                [plugin.metadata.name for plugin in plugins],
                ["good", "recovered"],
            )


if __name__ == "__main__":
    unittest.main()
