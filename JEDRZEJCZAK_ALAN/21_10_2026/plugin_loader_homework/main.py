"""Run the sample plugins: python main.py"""

from pathlib import Path

from plugin_loader import PluginError, PluginLoader, format_result


def main() -> int:
    folder = Path(__file__).resolve().parent / "plugins"
    loader = PluginLoader(folder)
    try:
        with loader.load() as plugins:
            for plugin in plugins:
                metadata = plugin.metadata
                print(f"{metadata.name} v{metadata.version}")
                print(f"  {format_result(plugin.run())}")
    except (PluginError, TypeError) as error:
        print(f"Plugin error: {error}")
        return 1
    print("All plugins cleaned up.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
