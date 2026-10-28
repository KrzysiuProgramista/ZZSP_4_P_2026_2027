import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

from plugin_loader import (
    PluginMetadata, discover_plugins, handle_result, loaded_plugins
)


PLUGIN_TEMPLATE = """
from dataclasses import dataclass
@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str
METADATA = PluginMetadata({name!r}, "1.0", "test plugin")
class Instance:
    def run(self, value):
        return value
    def close(self):
        with open({marker!r}, "w", encoding="utf-8") as f:
            f.write("closed")
def load():
    return Instance()
"""


class PluginLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_plugin(self, filename, source):
        path = self.folder / filename
        path.write_text(source, encoding="utf-8")
        return path

    def test_metadata_is_frozen(self):
        metadata = PluginMetadata("a", "1", "desc")
        with self.assertRaises(Exception):
            metadata.name = "changed"

    def test_discovery_finds_python_modules(self):
        self.write_plugin("a.py", "VALUE = 1")
        self.write_plugin("b.py", "VALUE = 2")
        self.write_plugin("__init__.py", "")
        self.assertEqual([p.name for p in discover_plugins(self.folder)], ["a.py", "b.py"])

    def test_valid_plugin_loads(self):
        self.write_plugin("good.py", PLUGIN_TEMPLATE.format(
            name="good", marker=str(self.folder / "closed.txt")))
        with loaded_plugins(self.folder) as plugins:
            self.assertEqual(len(plugins), 1)
            self.assertEqual(plugins[0].metadata.name, "good")

    def test_plugin_cleanup_after_normal_exit(self):
        marker = self.folder / "closed.txt"
        self.write_plugin("good.py", PLUGIN_TEMPLATE.format(name="good", marker=str(marker)))
        with loaded_plugins(self.folder):
            pass
        self.assertTrue(marker.exists())

    def test_plugin_cleanup_after_body_exception(self):
        marker = self.folder / "closed.txt"
        self.write_plugin("good.py", PLUGIN_TEMPLATE.format(name="good", marker=str(marker)))
        with self.assertRaisesRegex(ValueError, "body"):
            with loaded_plugins(self.folder):
                raise ValueError("body")
        self.assertTrue(marker.exists())

    def test_loader_recovers_when_plugin_load_raises(self):
        marker = self.folder / "closed.txt"
        self.write_plugin("a_good.py", PLUGIN_TEMPLATE.format(name="good", marker=str(marker)))
        self.write_plugin("z_failing.py", """
from dataclasses import dataclass
@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str
METADATA = PluginMetadata("failing", "1.0", "intentional failure")
def load():
    raise RuntimeError("intentional failure")
""")
        with self.assertRaisesRegex(RuntimeError, "intentional failure"):
            with loaded_plugins(self.folder):
                self.fail("context should not be entered")
        self.assertTrue(marker.exists())

    def test_invalid_interface_is_rejected(self):
        self.write_plugin("bad.py", """
from dataclasses import dataclass
@dataclass(frozen=True)
class Meta:
    name: str
    version: str
    description: str
METADATA = Meta("bad", "1", "bad")
def load():
    return object()
""")
        with self.assertRaisesRegex(TypeError, "run"):
            with loaded_plugins(self.folder):
                pass

    def test_cached_property_returns_same_cached_object(self):
        self.write_plugin("good.py", PLUGIN_TEMPLATE.format(
            name="good", marker=str(self.folder / "closed.txt")))
        with loaded_plugins(self.folder) as plugins:
            first = plugins[0].expensive_initialisation
            second = plugins[0].expensive_initialisation
            self.assertIs(first, second)

    def test_singledispatch_handles_supported_types(self):
        self.assertEqual(handle_result("ok"), "ok")
        self.assertEqual(handle_result(7), "Integer result: 7")
        self.assertEqual(handle_result([1, 2]), "List result with 2 item(s)")
        self.assertIn("keys: a", handle_result({"a": 1}))

    def test_unknown_result_type_has_fallback(self):
        self.assertIn("Unsupported result type", handle_result(2.5))


if __name__ == "__main__":
    unittest.main()
