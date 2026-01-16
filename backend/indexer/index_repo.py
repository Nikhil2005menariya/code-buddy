import sys
import chromadb
from backend.indexer.loader import load_repo_files
from backend.indexer.chunker import chunk_documents


def index_repo(repo_path: str, chroma_path: str):
    print(f"📂 Indexing repo: {repo_path}")
    print(f"🧠 Chroma path: {chroma_path}")

    # Load files
    docs = load_repo_files(repo_path)
    print(f"Loaded {len(docs)} files")

    # Chunk files
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")

    # Create project-specific Chroma DB
    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection("repo")

    collection.add(
        documents=[c["text"] for c in chunks],
        metadatas=[{"path": c["path"]} for c in chunks],
        ids=[f"chunk-{i}" for i in range(len(chunks))]
    )

    print("✅ Indexing completed")


if __name__ == "__main__":
    # Expecting:
    # python -m backend.indexer.index_repo <repo_path> <chroma_path>

    if len(sys.argv) != 3:
        print(
            "Usage:\n"
            "python -m backend.indexer.index_repo <repo_path> <chroma_path>"
        )
        sys.exit(1)

    repo_path = sys.argv[1]
    chroma_path = sys.argv[2]

    index_repo(repo_path, chroma_path)
