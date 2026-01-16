import difflib

def generate_diff(original: str, updated: str, path: str):
    diff = difflib.unified_diff(
        original.splitlines(),
        updated.splitlines(),
        fromfile=f"{path} (old)",
        tofile=f"{path} (new)",
        lineterm=""
    )
    return "\n".join(diff)
