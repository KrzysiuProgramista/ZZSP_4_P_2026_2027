"""An integer plugin with a calculation cached for the loaded instance."""

from plugin_loader import Plugin, PluginMetadata


class NumbersPlugin(Plugin):
    metadata = PluginMetadata("numbers", "1.0", "Calculate a sum of squares once")

    def initialize(self):
        return sum(number * number for number in range(1, 100_001))

    def run(self):
        return self.resource


PLUGIN_CLASS = NumbersPlugin
