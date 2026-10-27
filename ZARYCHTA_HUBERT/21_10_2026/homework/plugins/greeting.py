from tempfile import TemporaryFile
from plugin_loader import PluginMetadata

METADATA = PluginMetadata("greeting", "1.0", "Return text using a managed file")


def initialize(stack):
    # Register each resource immediately, before any later operation can fail.
    resource = stack.enter_context(TemporaryFile(mode="w+t"))
    resource.write("Hello from a plugin!")
    resource.seek(0)
    return resource


def run(state):
    state.seek(0)
    return state.read()


def cleanup():
    # The ExitStack owns the file; no extra module-level cleanup is needed.
    pass
