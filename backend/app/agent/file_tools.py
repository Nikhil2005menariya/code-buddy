import os

def read_file(path: str):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def write_file(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def file_exists(path: str):
    return os.path.exists(path)
