"""A mapping plugin demonstrating nested singledispatch results."""

from collections import Counter

from plugin_loader import Plugin, PluginMetadata


class SummaryPlugin(Plugin):
    metadata = PluginMetadata("summary", "1.0", "Cache word counts")

    def initialize(self):
        return Counter("python plugins python context managers".split())

    def run(self):
        return {
            "unique_words": len(self.resource),
            "python_count": self.resource["python"],
            "topics": list(self.resource),
        }


PLUGIN_CLASS = SummaryPlugin
