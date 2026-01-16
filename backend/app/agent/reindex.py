import subprocess
import sys
import os
import shutil
from app.config import CHROMA_BASE_DIR
from app.projects.repo import update_project_status


async def reindex_project(project_id: str, repo_path: str):
    """
    Starts repository indexing in a detached subprocess.
    Project status lifecycle:
    indexing -> ready | failed
    """

    chroma_path = os.path.join(CHROMA_BASE_DIR, project_id)

    # 1️⃣ Mark project as indexing
    await update_project_status(project_id, "indexing")

    # 2️⃣ Remove old index if exists
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    # 3️⃣ Start indexer as a DETACHED process (critical)
    subprocess.Popen(
        [
            sys.executable,
            os.path.join(os.getcwd(), "app/indexer/index_repo.py"),
            repo_path,
            chroma_path,
            project_id,  # pass project_id so indexer can update status
        ],
        start_new_session=True,   # 🔥 prevents SIGINT kill
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # ✅ DO NOT await completion here
    # ✅ DO NOT call update_project_status("ready") here
    # Indexer process is responsible for final status update
