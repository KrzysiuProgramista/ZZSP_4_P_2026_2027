from plugin_loader import PluginMetadata

METADATA = PluginMetadata("numbers", "1.0", "Cache an expensive calculation")


def initialize(stack):
    return sum(i * i for i in range(100_000))


def run(state):
    return state


def cleanup():
    pass
