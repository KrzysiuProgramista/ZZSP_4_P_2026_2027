from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, singledispatch
import importlib.util
import pathlib

@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str

class PluginInterface(ABC):
    metadata: PluginMetadata
    @abstractmethod
    def run(self):
        pass

class PluginContext:
    def __init__(self, plugins):
        self.plugins = plugins
        self.loaded = []

    def __enter__(self):
        try:
            for p in self.plugins:
                if hasattr(p, "initialize"):
                    p.initialize()
                self.loaded.append(p)
            return self
        except Exception:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        for p in reversed(self.loaded):
            try:
                if hasattr(p, "cleanup"):
                    p.cleanup()
            except Exception:
                pass

class PluginLoader:
    def load_from_folder(self, folder):
        plugins = []
        path = pathlib.Path(folder)
        for file_path in path.glob("*.py"):
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, PluginInterface) and attr is not PluginInterface:
                    plugins.append(attr())
        return plugins

@singledispatch
def process_result(result):
    return str(result)

@process_result.register
def _(result: int):
    return result + 10

@process_result.register
def _(result: str):
    return result.upper()