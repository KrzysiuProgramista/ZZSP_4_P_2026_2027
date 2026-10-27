"""A text plugin that caches a compiled regular expression."""

import re

from plugin_loader import Plugin, PluginMetadata


class WordsPlugin(Plugin):
    metadata = PluginMetadata("words", "1.0", "Find words using a cached pattern")

    def initialize(self):
        return re.compile(r"\b\w+\b")

    def run(self):
        words = self.resource.findall("Plugins make Python flexible")
        return " ".join(word.upper() for word in words)


PLUGIN_CLASS = WordsPlugin
