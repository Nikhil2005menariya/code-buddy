import os

from app.projects.repo import create_project
from app.agent.reindex import reindex_project


async def create_and_index_project(user_id: str, repo_path: str):
    """
    Create a project in MongoDB and index it immediately.
    Intended for internal / programmatic usage (not HTTP layer).
    """

    if not os.path.isdir(repo_path):
        raise ValueError("Invalid repository path")

    # ✅ Create project in MongoDB
    project = await create_project(
        user_id=user_id,
        repo_path=repo_path
    )

    # ✅ Run indexing (awaited, status-safe)
    await reindex_project(
        project_id=str(project["_id"]),
        repo_path=repo_path
    )

    return project
