"""Plugin that intentionally fails during initialisation for recovery tests."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str


METADATA = PluginMetadata(
    name="failing",
    version="1.0",
    description="Raises while loading",
)


def load():
    raise RuntimeError("Intentional plugin load failure")
