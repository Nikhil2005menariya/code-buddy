from app.projects.repo import get_project
from app.agent.repo_agent import ask_repo
from app.chat.pending_actions import set_pending_action
from app.chat.repo import (
    add_chat_message,
    get_recent_chat_context,
)


async def chat_with_project(
    project_id: str,
    message: str,
    user_id: str
):
    # 1️⃣ Verify project ownership
    project = await get_project(project_id, user_id)
    if not project:
        raise ValueError("Project not found or access denied")

    # 2️⃣ Persist USER message
    await add_chat_message(
        project_id=project_id,
        user_id=user_id,
        role="user",
        content=message
    )

    # 3️⃣ Fetch recent chat context (last N messages)
    recent_history = await get_recent_chat_context(
        project_id=project_id,
        user_id=user_id,
        limit=6
    )

    # 4️⃣ Ask repo-aware agent WITH chat context
    response = ask_repo(
        question=message,
        project_id=project_id,
        repo_path=project["repo_path"],
        chat_history=recent_history
    )

    # 5️⃣ Agent proposes a code change
    if response.strip().startswith("ACTION:"):
        set_pending_action(project_id, response)

        await add_chat_message(
            project_id=project_id,
            user_id=user_id,
            role="agent",
            content=response
        )

        return {
            "type": "action",
            "message": "Agent proposes a code change",
            "raw_response": response
        }

    # 6️⃣ Normal explanation response
    await add_chat_message(
        project_id=project_id,
        user_id=user_id,
        role="agent",
        content=response
    )

    return {
        "type": "explanation",
        "message": response
    }
