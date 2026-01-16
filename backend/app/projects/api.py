from fastapi import APIRouter, BackgroundTasks, Depends
from app.auth.deps import get_current_user
from app.projects.repo import create_project, list_projects
from app.agent.reindex import reindex_project

router = APIRouter(prefix="/projects")


@router.post("/new")
async def new_project(
    repo_path: str,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    project = await create_project(
        user_id=user["user_id"],
        repo_path=repo_path
    )

    # ✅ Correct: schedule async background task
    background_tasks.add_task(
        reindex_project,
        str(project["_id"]),
        repo_path
    )

    return {
        "id": str(project["_id"]),
        "repo_path": repo_path,
        "status": "indexing_started"
    }


@router.get("/")
async def my_projects(user=Depends(get_current_user)):
    projects = await list_projects(user["user_id"])

    return [
        {
            "id": str(p["_id"]),
            "repo_path": p["repo_path"],
            "status": p["status"]
        }
        for p in projects
    ]
