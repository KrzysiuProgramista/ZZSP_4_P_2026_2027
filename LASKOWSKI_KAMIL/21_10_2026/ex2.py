import sqlite3
import os
from contextlib import contextmanager
import tempfile
import shutil

@contextmanager
def db_transaction(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def change_directory(new_path):
    original_path = os.getcwd()
    os.chdir(new_path)
    try:
        yield
    finally:
        os.chdir(original_path)

@contextmanager
def temporary_directory():
    dir_path = tempfile.mkdtemp()
    try:
        yield dir_path
    finally:
        shutil.rmtree(dir_path)