"""Ten tests for discovery, validation, resource ownership, and result dispatch."""

import dataclasses
from pathlib import Path
import sys
import tempfile
import textwrap
import types
import unittest
import uuid

from plugin_loader import (
    Plugin,
    PluginLoadError,
    PluginLoader,
    PluginMetadata,
    PluginValidationError,
    format_result,
)


class PluginLoaderTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.folder = Path(self.temporary_directory.name)

        # Plugins import this small in-memory module to report observable events.
        self.state_name = "_homework_test_state_" + uuid.uuid4().hex
        self.state = types.ModuleType(self.state_name)
        self.state.events = []
        self.state.resources = []
        sys.modules[self.state_name] = self.state
        self.addCleanup(sys.modules.pop, self.state_name, None)
        self.original_plugin_modules = self._plugin_modules()

    @staticmethod
    def _plugin_modules():
        return {
            name for name in sys.modules if name.startswith("_homework_plugin_")
        }

    def _assert_no_module_leaks(self):
        self.assertEqual(self._plugin_modules(), self.original_plugin_modules)

    def _write_source(self, filename, source, folder=None):
        destination = (folder or self.folder) / filename
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(textwrap.dedent(source), encoding="utf-8")
        return destination

    def _write_plugin(self, filename, overrides="", folder=None):
        label = Path(filename).stem
        source = textwrap.dedent(
            f"""\
            from plugin_loader import Plugin, PluginMetadata
            from {self.state_name} import events, resources

            class ExamplePlugin(Plugin):
                metadata = PluginMetadata({label!r}, "1.0", "Test plugin")

                def initialize(self):
                    events.append({label!r} + ":initialize")
                    return object()

                def run(self):
                    return {label!r}

                def cleanup(self):
                    events.append({label!r} + ":cleanup")
                    super().cleanup()
            """
        )
        if overrides:
            source += "\n" + textwrap.indent(textwrap.dedent(overrides), "    ")
        source += "\n\nPLUGIN_CLASS = ExamplePlugin\n"
        return self._write_source(filename, source, folder)

    def test_01_discovery_is_sorted_filtered_and_happens_at_runtime(self):
        self._write_plugin("b_second.py")
        self._write_plugin("a_first.py")
        self._write_plugin("_private.py")
        self._write_source("__init__.py", "")
        self._write_source("notes.txt", "This is not a Python plugin.")
        self._write_plugin("nested/hidden.py")
        loader = PluginLoader(self.folder)

        self.assertEqual(
            loader.discover(),
            (self.folder / "a_first.py", self.folder / "b_second.py"),
        )

        # The loader must rescan; no sleeps or timestamp manipulation are needed.
        self._write_plugin("c_added_later.py")
        self.assertEqual(
            tuple(path.name for path in loader.discover()),
            ("a_first.py", "b_second.py", "c_added_later.py"),
        )

    def test_02_valid_plugins_load_and_run(self):
        self._write_plugin("a_first.py")
        self._write_plugin("b_second.py")

        with PluginLoader(self.folder).load() as plugins:
            self.assertIsInstance(plugins, tuple)
            self.assertEqual(len(plugins), 2)
            self.assertTrue(all(isinstance(plugin, Plugin) for plugin in plugins))
            self.assertEqual(
                [plugin.run() for plugin in plugins], ["a_first", "b_second"]
            )
            self.assertEqual(plugins[0].metadata.name, "a_first")
            self.assertEqual(
                self.state.events, ["a_first:initialize", "b_second:initialize"]
            )

        self._assert_no_module_leaks()

    def test_03_invalid_interfaces_are_rejected(self):
        invalid_sources = {
            "missing_export": "VALUE = 1\n",
            "nonclass_export": "PLUGIN_CLASS = 42\n",
            "wrong_base": "class Wrong: pass\nPLUGIN_CLASS = Wrong\n",
            "abstract_class": (
                "from plugin_loader import Plugin, PluginMetadata\n"
                "class Incomplete(Plugin):\n"
                "    metadata = PluginMetadata('Incomplete', '1.0')\n"
                "PLUGIN_CLASS = Incomplete\n"
            ),
        }
        for label, source in invalid_sources.items():
            with self.subTest(case=label):
                folder = self.folder / label
                self._write_source("invalid.py", source, folder)
                with self.assertRaises(PluginValidationError):
                    with PluginLoader(folder).load():
                        self.fail("An invalid interface was loaded.")
                self._assert_no_module_leaks()

        for hook in ("initialize", "setup", "run", "cleanup"):
            for variant in ("noncallable", "required_argument"):
                with self.subTest(hook=hook, variant=variant):
                    folder = self.folder / (hook + "_" + variant)
                    if variant == "noncallable":
                        override = f"{hook} = None\n"
                    else:
                        override = f"def {hook}(self, required):\n    return required\n"
                    self._write_plugin("invalid.py", override, folder)
                    with self.assertRaises(PluginValidationError):
                        with PluginLoader(folder).load():
                            self.fail("An incompatible hook was loaded.")
                    self._assert_no_module_leaks()

        with self.subTest(case="constructor_requires_argument"):
            folder = self.folder / "invalid_constructor"
            self._write_plugin(
                "invalid.py", "def __init__(self, required):\n    pass\n", folder
            )
            with self.assertRaises(PluginValidationError):
                with PluginLoader(folder).load():
                    self.fail("An incompatible constructor was loaded.")
            self._assert_no_module_leaks()

    def test_04_invalid_metadata_is_rejected(self):
        invalid_fields = (
            {"name": "", "version": "1.0"},
            {"name": "   ", "version": "1.0"},
            {"name": 7, "version": "1.0"},
            {"name": "Example", "version": ""},
            {"name": "Example", "version": "  "},
            {"name": "Example", "version": 1},
            {"name": "Example", "version": "1.0", "description": None},
        )
        for fields in invalid_fields:
            with self.subTest(fields=fields):
                with self.assertRaises((TypeError, ValueError)):
                    PluginMetadata(**fields)

        self._write_plugin(
            "invalid.py", "metadata = {'name': 'Example', 'version': '1.0'}\n"
        )
        with self.assertRaises(PluginValidationError):
            with PluginLoader(self.folder).load():
                self.fail("A dictionary is not PluginMetadata.")
        self._assert_no_module_leaks()

    def test_05_metadata_is_a_frozen_dataclass(self):
        metadata = PluginMetadata("Example", "1.0", "Description")
        self.assertTrue(dataclasses.is_dataclass(metadata))
        self.assertTrue(metadata.__dataclass_params__.frozen)
        self.assertEqual(metadata, PluginMetadata("Example", "1.0", "Description"))
        self.assertEqual(PluginMetadata("Example", "1.0").description, "")

        with self.assertRaises(dataclasses.FrozenInstanceError):
            metadata.name = "Changed"
        with self.assertRaises(dataclasses.FrozenInstanceError):
            metadata.version = "2.0"

    def test_06_exit_cleans_in_reverse_order_even_if_cleanup_raises(self):
        for failing_cleanup in (False, True):
            with self.subTest(failing_cleanup=failing_cleanup):
                self.state.events.clear()
                folder = self.folder / str(failing_cleanup)
                self._write_plugin("a_first.py", folder=folder)
                override = ""
                if failing_cleanup:
                    override = """\
                    def cleanup(self):
                        events.append("b_second:cleanup")
                        super().cleanup()
                        raise RuntimeError("cleanup exploded")
                    """
                self._write_plugin("b_second.py", override, folder)
                self._write_plugin("c_third.py", folder=folder)

                def enter_and_leave():
                    with PluginLoader(folder).load() as plugins:
                        self.assertEqual(len(plugins), 3)
                        self.assertTrue(
                            self._plugin_modules() - self.original_plugin_modules
                        )

                if failing_cleanup:
                    with self.assertRaisesRegex(RuntimeError, "cleanup exploded"):
                        enter_and_leave()
                else:
                    enter_and_leave()

                self.assertEqual(
                    [event for event in self.state.events if event.endswith(":cleanup")],
                    ["c_third:cleanup", "b_second:cleanup", "a_first:cleanup"],
                )
                self._assert_no_module_leaks()

    def test_07_body_exception_propagates_and_cleanup_still_runs(self):
        self._write_plugin("a_first.py")
        self._write_plugin("b_second.py")
        original_error = RuntimeError("failure in the caller")

        with self.assertRaises(RuntimeError) as caught:
            with PluginLoader(self.folder).load():
                raise original_error

        self.assertIs(caught.exception, original_error)
        self.assertEqual(
            [event for event in self.state.events if event.endswith(":cleanup")],
            ["b_second:cleanup", "a_first:cleanup"],
        )
        self._assert_no_module_leaks()

    def test_08_loading_failure_closes_real_resources_and_loader_recovers(self):
        def resource_hooks(label, fail_during_setup=False):
            resource_path = str(self.folder / (label + ".txt"))
            hooks = f"""\
            def initialize(self):
                handle = open({resource_path!r}, "w", encoding="utf-8")
                resources.append(handle)
                events.append({label!r} + ":initialize")
                return handle

            def cleanup(self):
                events.append({label!r} + ":cleanup")
                if "resource" in self.__dict__:
                    self.__dict__["resource"].close()
                super().cleanup()
            """
            if fail_during_setup:
                hooks = textwrap.dedent(hooks) + "\n" + textwrap.dedent(
                    """\
                    def setup(self):
                        super().setup()
                        raise RuntimeError("broken setup")
                    """
                )
            return hooks

        self._write_plugin("a_good.py", resource_hooks("a_good"))
        broken_path = self._write_plugin(
            "b_broken.py", resource_hooks("b_broken", fail_during_setup=True)
        )
        loader = PluginLoader(self.folder)

        with self.assertRaises(PluginLoadError) as caught:
            with loader.load():
                self.fail("A failed setup must prevent entering the context.")

        self.assertIsInstance(caught.exception.__cause__, RuntimeError)
        self.assertEqual(str(caught.exception.__cause__), "broken setup")
        self.assertEqual(len(self.state.resources), 2)
        self.assertTrue(all(handle.closed for handle in self.state.resources))
        self.assertEqual(
            [event for event in self.state.events if event.endswith(":cleanup")],
            ["b_broken:cleanup", "a_good:cleanup"],
        )
        self._assert_no_module_leaks()

        # Reuse the same loader after removing the faulty plugin.
        broken_path.unlink()
        with loader.load() as plugins:
            self.assertEqual(len(plugins), 1)
            self.assertEqual(plugins[0].run(), "a_good")
            self.assertFalse(self.state.resources[-1].closed)

        self.assertEqual(len(self.state.resources), 3)
        self.assertTrue(all(handle.closed for handle in self.state.resources))
        self._assert_no_module_leaks()

        # Earlier plugins must also be unwound for other loading failures.
        for stage in ("import", "constructor", "initialize"):
            with self.subTest(failure_stage=stage):
                self.state.events.clear()
                self.state.resources.clear()
                folder = self.folder / (stage + "_failure")
                self._write_plugin("a_good.py", resource_hooks("a_good"), folder)
                if stage == "import":
                    broken_path = self._write_source(
                        "b_broken.py", "raise RuntimeError('broken import')\n", folder
                    )
                elif stage == "constructor":
                    broken_path = self._write_plugin(
                        "b_broken.py",
                        "def __init__(self):\n"
                        "    raise RuntimeError('broken constructor')\n",
                        folder,
                    )
                else:
                    resource_path = str(self.folder / "b_initialize.txt")
                    broken_path = self._write_plugin(
                        "b_broken.py",
                        f"""\
                        def initialize(self):
                            # cached_property cannot cache a value that never returns.
                            # Keep a reference early so cleanup can release it anyway.
                            self.pending_handle = open(
                                {resource_path!r}, "w", encoding="utf-8"
                            )
                            resources.append(self.pending_handle)
                            events.append("b_broken:initialize")
                            raise RuntimeError("broken initialize")

                        def cleanup(self):
                            events.append("b_broken:cleanup")
                            handle = self.__dict__.pop("pending_handle", None)
                            if handle is not None:
                                handle.close()
                            super().cleanup()
                        """,
                        folder,
                    )
                loader = PluginLoader(folder)

                with self.assertRaises(PluginLoadError) as caught:
                    with loader.load():
                        self.fail("The loading failure should propagate.")

                self.assertIsInstance(caught.exception.__cause__, RuntimeError)
                self.assertEqual(str(caught.exception.__cause__), "broken " + stage)
                expected_acquired = 2 if stage == "initialize" else 1
                self.assertEqual(len(self.state.resources), expected_acquired)
                self.assertTrue(all(handle.closed for handle in self.state.resources))
                expected_cleanup = ["a_good:cleanup"]
                if stage == "initialize":
                    expected_cleanup.insert(0, "b_broken:cleanup")
                self.assertEqual(
                    [event for event in self.state.events if event.endswith(":cleanup")],
                    expected_cleanup,
                )
                self._assert_no_module_leaks()

                broken_path.unlink()
                with loader.load() as plugins:
                    self.assertEqual(len(plugins), 1)
                    self.assertEqual(plugins[0].run(), "a_good")
                    self.assertFalse(self.state.resources[-1].closed)

                self.assertEqual(len(self.state.resources), expected_acquired + 1)
                self.assertTrue(all(handle.closed for handle in self.state.resources))
                self._assert_no_module_leaks()

    def test_09_cached_property_is_lazy_and_initializes_once_per_instance(self):
        calls = []

        class ExpensivePlugin(Plugin):
            metadata = PluginMetadata("Expensive", "1.0")

            def initialize(self):
                calls.append("initialized")
                return object()

            def run(self):
                return self.resource

        plugin = ExpensivePlugin()
        self.assertEqual(calls, [])
        self.assertNotIn("resource", plugin.__dict__)

        first_resource = plugin.resource
        self.assertIs(plugin.resource, first_resource)
        self.assertIs(plugin.run(), first_resource)
        plugin.setup()
        self.assertEqual(calls, ["initialized"])

        second_plugin = ExpensivePlugin()
        self.assertIsNot(second_plugin.resource, first_resource)
        self.assertEqual(calls, ["initialized", "initialized"])

        plugin.cleanup()
        second_plugin.cleanup()
        self.assertNotIn("resource", plugin.__dict__)
        self.assertNotIn("resource", second_plugin.__dict__)

    def test_10_singledispatch_formats_supported_types_and_rejects_others(self):
        cases = (
            ("hi", "Text: hi"),
            (7, "Integer: 7"),
            (0, "Integer: 0"),
            (2.5, "Float: 2.5"),
            (2.0, "Float: 2"),
            (True, "Boolean: true"),
            (False, "Boolean: false"),
            (None, "No result"),
            ([], "List: []"),
            ([1, "hi"], "List: [Integer: 1, Text: hi]"),
            ({}, "Mapping: {}"),
            (
                {"answer": 7, "items": ["hi", None]},
                "Mapping: {'answer': Integer: 7, 'items': List: [Text: hi, No result]}",
            ),
            ({2: True}, "Mapping: {2: Boolean: true}"),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(format_result(value), expected)

        for value in ((), {1, 2}, object()):
            with self.subTest(unsupported_type=type(value).__name__):
                with self.assertRaises(TypeError):
                    format_result(value)


if __name__ == "__main__":
    unittest.main()
