from fastapi import APIRouter, Depends, HTTPException

from app.models import ChatRequest
from app.auth.deps import get_current_user
from app.chat.service import chat_with_project

from app.chat.pending_actions import (
    get_pending_action,
    clear_pending_action
)

from app.agent.repo_agent import apply_agent_response
from app.projects.repo import get_project
from app.agent.reindex import reindex_project
from app.chat.repo import update_agent_message



router = APIRouter(prefix="/chat")


@router.post("/")
async def chat(
    req: ChatRequest,
    user=Depends(get_current_user)
):
    """
    Chat with a project.
    - Requires authentication
    - Project must belong to the user
    """
    return await chat_with_project(
        project_id=req.project_id,
        message=req.message,
        user_id=user["user_id"]
    )



@router.post("/apply/{project_id}")
async def apply_change(
    project_id: str,
    user=Depends(get_current_user)
):
    pending = get_pending_action(project_id)
    if not pending:
        raise HTTPException(status_code=400, detail="No pending action")

    project = await get_project(project_id, user["user_id"])
    if not project:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    result = await apply_agent_response(
        pending,
        project_id,
        project["repo_path"]
    )

    # ✅ PERSIST AGENT ACTION
    await update_agent_message(
        project_id,
        pending,                    # ← raw agent text
        status="applied",
        diff=result.get("diff")
    )


    clear_pending_action(project_id)

    return result



from app.chat.repo import update_agent_message
from app.chat.repo import get_chat_history

@router.post("/reject/{project_id}")
async def reject_change(
    project_id: str,
    user=Depends(get_current_user)
):
    pending = get_pending_action(project_id)
    if not pending:
        raise HTTPException(status_code=400, detail="No pending action")

    project = await get_project(project_id, user["user_id"])
    if not project:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    await update_agent_message(
        project_id,
        pending,
        status="rejected"
    )


    clear_pending_action(project_id)

    return {"status": "rejected"}



@router.post("/reindex/{project_id}")
async def reindex(
    project_id: str,
    user=Depends(get_current_user)
):
    """
    Manually reindex a project (e.g. after user edits files locally).
    """
    project = await get_project(project_id, user["user_id"])
    if not project:
        raise HTTPException(status_code=403, detail="Access denied to this project")

    await reindex_project(
        project_id,
        project["repo_path"]
    )

    return {"status": "reindexing_started"}



@router.get("/history/{project_id}")
async def chat_history(
    project_id: str,
    user=Depends(get_current_user)
):
    project = await get_project(project_id, user["user_id"])
    if not project:
        raise HTTPException(status_code=403, detail="Access denied")

    history = await get_chat_history(
        project_id,
        user["user_id"]
    )

    return {
        "project_id": project_id,
        "messages": history
    }

