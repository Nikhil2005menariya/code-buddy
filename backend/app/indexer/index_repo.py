import sys
import os
import chromadb
import traceback
from pymongo import MongoClient
from bson import ObjectId


IGNORE_DIRS = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".next",
    ".venv",
    "__pycache__",
    ".idea",
    ".vscode",
}

ALLOWED_EXTENSIONS = (
    # JavaScript / TypeScript
    ".js", ".ts", ".tsx", ".jsx",

    # Python
    ".py",

    # Backend / APIs
    ".java", ".kt", ".go", ".rs",

    # Web
    ".html", ".css", ".scss",

    # Config
    ".json", ".yaml", ".yml", ".toml", ".ini",

    # Shell / DevOps
    ".sh", ".bash", ".zsh", ".ps1",
    ".dockerfile", "Dockerfile",

    # Docs
    ".md", ".txt",

    # SQL
    ".sql"
)



def update_status(project_id: str, status: str):
    client = MongoClient("mongodb://localhost:27017")
    db = client["repo_agent"]
    projects = db["projects"]

    projects.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"status": status}}
    )


def index_repo(repo_path: str, chroma_path: str, project_id: str):
    client = chromadb.PersistentClient(path=chroma_path)
    try:
        client.delete_collection("repo")
    except Exception:
        pass


    collection = client.get_or_create_collection("repo")

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        for file in files:
            if not file.endswith(ALLOWED_EXTENSIONS):
                continue

            path = os.path.join(root, file)

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()

                if not content:
                    continue

                doc_id = f"{project_id}:{path}"

                collection.add(
                    documents=[content],
                    metadatas=[{"path": path}],
                    ids=[doc_id],
                )

            except Exception:
                continue


if __name__ == "__main__":
    repo_path = sys.argv[1]
    chroma_path = sys.argv[2]
    project_id = sys.argv[3]

    try:
        update_status(project_id, "indexing")
        index_repo(repo_path, chroma_path, project_id)
        update_status(project_id, "ready")
    except Exception:
        update_status(project_id, "failed")
        traceback.print_exc()
