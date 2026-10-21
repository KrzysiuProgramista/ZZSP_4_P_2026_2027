from contextlib import ExitStack
from contextlib import suppress
from contextlib import closing
import urllib.request
import os

with open("file1.txt", "w") as f1, open("file2.txt", "w") as f2:
  f1.write("hello from file 1")
  f2.write("hello from file 2")

file_paths = ["file1.txt", "file2.txt", "file3.txt"]


with ExitStack() as stack:
  files = [stack.enter_context(open(path, "r")) for path in file_paths]


  for i, f in enumerate(files):
    print(f"content of file {i+1}: {f.read()}")
  for path in file_paths:
    if os.path.exists(path):
      f = stack.enter_context(open(path, "r"))
      print(f.read())
    else:
      print(f"skipping {path} (does not exist)")


with suppress(FileNotFoundError):
  os.remove("nonexistent_file.txt")



with closing(urllib.request.urlopen("https://example.com")) as response:
  html_content = response.read()
  print(f"downloaded {len(html_content)} bytes.")
