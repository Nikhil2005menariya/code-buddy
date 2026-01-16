import os

IGNORE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    "__pycache__",
    ".venv",
    "venv"
}

ALLOWED_EXTENSIONS = (
    ".py", ".js", ".ts", ".tsx",
    ".jsx", ".json", ".md", ".yml", ".yaml"
)

def load_repo_files(repo_path: str):
    documents = []

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if file.endswith(ALLOWED_EXTENSIONS):
                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        documents.append({
                            "path": path,
                            "content": f.read()
                        })
                except Exception as e:
                    print(f"Skipped {path}: {e}")

    return documents
