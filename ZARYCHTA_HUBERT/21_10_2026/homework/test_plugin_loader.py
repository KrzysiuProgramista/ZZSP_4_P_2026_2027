from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import textwrap
from types import ModuleType
import unittest

from plugin_loader import (PluginLoader, PluginMetadata, PluginValidationError,
                           discover_plugins, handle_result, validate_plugin)


class PluginLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.log = self.folder / "events.txt"
        self.loader = PluginLoader(self.folder)

    def write_plugin(self, name="sample", *, fail_init=False, fail_cleanup=False):
        source = f'''
from pathlib import Path
from tempfile import TemporaryFile
from plugin_loader import PluginMetadata
METADATA = PluginMetadata({name!r}, "1.0")
LOG = Path({str(self.log)!r})
calls = 0
resource = None

def event(message):
    with LOG.open("a") as output:
        output.write(message + "\\n")

def initialize(stack):
    global calls, resource
    calls += 1
    resource = stack.enter_context(TemporaryFile(mode="w+t"))
    stack.callback(event, {name!r} + ":resource-released")
    event({name!r} + ":init")
    if {fail_init!r}:
        raise RuntimeError("initialization failed")
    return resource

def run(state):
    assert not state.closed
    return "hello"

def cleanup():
    event({name!r} + ":cleanup:closed=" + str(resource.closed))
    if {fail_cleanup!r}:
        raise RuntimeError("cleanup failed")
'''
        path = self.folder / f"{name}.py"
        path.write_text(textwrap.dedent(source), encoding="utf-8")
        return path

    def runtime_modules(self):
        return {name for name in sys.modules if name.startswith("_runtime_plugin_")}

    def test_01_discovery_is_sorted_and_ignores_non_plugins(self):
        self.write_plugin("b")
        self.write_plugin("a")
        (self.folder / "_private.py").touch()
        (self.folder / "notes.txt").touch()
        (self.folder / "directory.py").mkdir()
        self.assertEqual([p.name for p in discover_plugins(self.folder)], ["a.py", "b.py"])
        with self.assertRaises(NotADirectoryError):
            discover_plugins(self.folder / "missing")

    def test_02_metadata_is_frozen_and_validated(self):
        metadata = PluginMetadata("example", "1.0")
        with self.assertRaises(FrozenInstanceError):
            metadata.name = "changed"
        for name, version in (("", "1.0"), ("example", 1)):
            with self.assertRaises(ValueError):
                PluginMetadata(name, version)

    def test_03_interface_rejects_missing_members_and_bad_signatures(self):
        for defect in ("metadata", "missing", "signature", "async"):
            with self.subTest(defect=defect):
                module = ModuleType("invalid")
                module.METADATA = PluginMetadata("test", "1.0")
                module.initialize = lambda stack: None
                module.run = lambda state: "ok"
                module.cleanup = lambda: None
                if defect == "metadata":
                    module.METADATA = {"name": "wrong"}
                elif defect == "missing":
                    del module.cleanup
                elif defect == "signature":
                    module.run = lambda: "wrong"
                else:
                    async def async_run(state):
                        return state
                    module.run = async_run
                with self.assertRaises(PluginValidationError):
                    validate_plugin(module)

    def test_04_success_runs_and_closes_resources_and_unloads_modules(self):
        self.write_plugin()
        before = self.runtime_modules()
        with self.loader.load() as plugins:
            plugin = plugins[0]
            resource = plugin.state
            self.assertEqual(plugin.run(), "Text: hello")
            self.assertFalse(resource.closed)
        self.assertTrue(resource.closed)
        self.assertEqual(self.runtime_modules(), before)
        with self.assertRaises(RuntimeError):
            plugin.run()
        with self.assertRaises(RuntimeError):
            _ = plugin.state

    def test_05_cached_initialization_runs_once_per_session(self):
        self.write_plugin()
        with self.loader.load() as plugins:
            plugin = plugins[0]
            self.assertIs(plugin.state, plugin.state)
            plugin.run()
            plugin.run()
            self.assertEqual(plugin.module.calls, 1)
        with self.loader.load() as plugins:
            self.assertEqual(plugins[0].module.calls, 1)
        self.assertEqual(self.log.read_text().count("sample:init"), 2)

    def test_06_singledispatch_handles_supported_and_unknown_types(self):
        for value, expected in (("hello", "Text: hello"), (7, "Number: 7"),
                                (2.5, "Number: 2.5"), ([1, 2], "[1, 2]"),
                                ({"x": 1}, '{"x": 1}')):
            with self.subTest(value=value):
                self.assertEqual(handle_result(value), expected)
        with self.assertRaises(TypeError):
            handle_result(object())

    def test_07_initialization_failure_rolls_back_and_loader_recovers(self):
        self.write_plugin("a_good")
        broken = self.write_plugin("b_bad", fail_init=True)
        before = self.runtime_modules()
        with self.assertRaisesRegex(RuntimeError, "initialization failed"):
            with self.loader.load():
                self.fail("The context body must not run")
        self.assertEqual(self.runtime_modules(), before)
        events = self.log.read_text().splitlines()
        self.assertEqual(events, ["a_good:init", "b_bad:init",
            "b_bad:resource-released", "b_bad:cleanup:closed=True",
            "a_good:resource-released", "a_good:cleanup:closed=True"])
        broken.unlink()
        with self.loader.load() as plugins:
            self.assertEqual(plugins[0].run(), "Text: hello")

    def test_08_body_exception_still_cleans_up(self):
        self.write_plugin()
        before = self.runtime_modules()
        with self.assertRaisesRegex(RuntimeError, "body failed"):
            with self.loader.load() as plugins:
                resource = plugins[0].state
                raise RuntimeError("body failed")
        self.assertTrue(resource.closed)
        self.assertEqual(self.runtime_modules(), before)

    def test_09_import_and_validation_failures_roll_back_prior_plugins(self):
        self.write_plugin("a_good")
        bad = self.folder / "z_bad.py"
        for source, error in (("raise RuntimeError('import failed')", RuntimeError),
                              ("METADATA = None", PluginValidationError)):
            with self.subTest(source=source):
                bad.write_text(source)
                before = self.runtime_modules()
                with self.assertRaises(error):
                    with self.loader.load():
                        self.fail("Must not enter")
                self.assertEqual(self.runtime_modules(), before)
                self.assertTrue(self.log.read_text().endswith("a_good:cleanup:closed=True\n"))

    def test_10_cleanup_error_does_not_skip_remaining_cleanup(self):
        self.write_plugin("a_good")
        self.write_plugin("b_bad", fail_cleanup=True)
        before = self.runtime_modules()
        with self.assertRaisesRegex(RuntimeError, "cleanup failed"):
            with self.loader.load() as plugins:
                resources = [plugin.state for plugin in plugins]
        self.assertTrue(all(resource.closed for resource in resources))
        self.assertEqual(self.runtime_modules(), before)
        self.assertTrue(self.log.read_text().endswith("a_good:cleanup:closed=True\n"))


if __name__ == "__main__":
    unittest.main()
