import os
from contextlib import contextmanager
import os
import shutil

class ConnectionScope:
    def __init__(self, connect):
        self.connect = connect

    def __enter__(self):
        self.connection = self.connect()
        return self.connection

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                self.connection.rollback()
        finally:
            self.connection.close()
        return False

@contextmanager
def temporary_env(name, value):
    existed = name in os.environ
    old = os.environ.get(name)
    os.environ[name] = value
    try:
        yield
    finally:
        if existed:
            os.environ[name] = old
        else:
            os.environ.pop(name, None)

class TempDir:
    def __init__(self, dirname):
        self.dir = dirname

    def __enter__(self):
          os.mkdir(self.dir)
    def __exit__(self, exc_type, exc, tb):
        if os.path.exists(self.dir):
            shutil.rmtree(self.dir)
        return False 


@contextmanager
def change_dir(destination):
    original_dir = os.getcwd()
    os.chdir(destination)
    try:
        yield
    finally:
        os.chdir(original_dir)

