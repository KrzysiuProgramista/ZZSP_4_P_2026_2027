import os
import shutil
import tempfile
from contextlib import contextmanager

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
def temporary_directory():
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        shutil.rmtree(tmp_dir)

@contextmanager
def change_directory(path):
    prev_dir = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_dir)

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