"""Example plugin discovered by the plugin loader."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str


METADATA = PluginMetadata(
    name="example",
    version="1.0",
    description="A simple example plugin",
)


def load():
    """Called by the loader to initialise this plugin."""
    return ExamplePlugin()


class ExamplePlugin:
    def run(self, value):
        if isinstance(value, int):
            return value * 2
        if isinstance(value, str):
            return value.upper()
        return {"received": value}

    def close(self):
        """Release resources held by the plugin."""
        pass
