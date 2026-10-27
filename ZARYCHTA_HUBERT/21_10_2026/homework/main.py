from pathlib import Path
from plugin_loader import PluginLoader


def main():
    loader = PluginLoader(Path(__file__).parent / "plugins")
    with loader.load() as plugins:
        for plugin in plugins:
            print(f"{plugin.metadata.name} v{plugin.metadata.version}: {plugin.run()}")


if __name__ == "__main__":
    main()
