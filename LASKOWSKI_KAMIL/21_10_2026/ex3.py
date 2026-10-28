from contextlib import ExitStack
import os
from contextlib import suppress, closing

def open_multiple_files(file_paths):
    with ExitStack() as stack:
        files = [stack.enter_context(open(path, "w")) for path in file_paths]
        
        for f in files:
            f.write("Data entry\n")

with suppress(FileNotFoundError):
    os.remove("non_existent_file.txt")
print("Execution continues smoothly without crashing.")

with open("source.txt", "w") as src, open("destination.txt", "w") as dest:
    src.write("Hello, World!")
    dest.write(src.name)

try:
    os.remove("non_existent_file.txt")
except FileNotFoundError:
    pass

class LegacyDatabaseConnection:
    def connect(self):
        print("Connected to legacy database.")
    
    def close(self):
        print("Legacy database connection closed safely.")

with closing(LegacyDatabaseConnection()) as db:
    db.connect()
    print("Performing database operations...")