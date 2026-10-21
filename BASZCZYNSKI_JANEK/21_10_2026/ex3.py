import contextlib
import os

def twoManagers():
    with open('file1.txt', 'w') as f1, open('file2.txt', 'w') as f2:
        f1.write("Hello from file 1!")
        f2.write("Hello from file 2!")


def variableFileNames():
    filenames = ['file1.txt', 'file2.txt', 'file3.txt']

    with contextlib.ExitStack() as stack:
        open_files = [stack.enter_context(open(fname, 'w')) for fname in filenames]
        
        for i, f in enumerate(open_files):
            f.write(f"Content for file {i+1}\n")


def supress():

    # Option A
    with contextlib.suppress(FileNotFoundError):
        os.remove("temp_file.txt")
        print("File deleted successfully.")



    # Option B
    try:
        os.remove("temp_file.txt")
        print("File deleted successfully.")
    except FileNotFoundError:
        pass

    # Option A is clearer and prevents repeating the code if used in many places

class SimpleConnection:
    def connect(self):
        print("Connected to the server.")
        
    def close(self):
        print("Connection closed safely!")

def contextClosing():
    with contextlib.closing(SimpleConnection()) as conn:
        conn.connect()


    