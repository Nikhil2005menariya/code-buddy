from datetime import datetime
from bson import ObjectId
from app.db.mongo import agent_messages_collection
from typing import Optional,List


async def save_user_message(user_id: str, project_id: str, message: str):
    await agent_messages_collection.insert_one({
        "user_id": ObjectId(user_id),
        "project_id": ObjectId(project_id),
        "role": "user",
        "type": "explanation",
        "message": message,
        "raw_response": None,
        "status": None,
        "diff": None,
        "created_at": datetime.utcnow()
    })


async def save_agent_message(
    user_id: str,
    project_id: str,
    *,
    message: str,
    raw_response: str = None,
    msg_type: str,
    status: str = None
):
    await agent_messages_collection.insert_one({
        "user_id": ObjectId(user_id),
        "project_id": ObjectId(project_id),
        "role": "agent",
        "type": msg_type,
        "message": message,
        "raw_response": raw_response,
        "status": status,
        "diff": None,
        "created_at": datetime.utcnow()
    })



async def add_chat_message(
    project_id: str,
    user_id: str,
    role: str,
    content: str
):
    await agent_messages_collection.insert_one({
        "project_id": ObjectId(project_id),
        "user_id": ObjectId(user_id),
        "role": role,
        "content": content,
        "status": None,
        "diff": None,
        "created_at": datetime.utcnow()
    })


async def update_agent_message(
    project_id: str,
    content: str,
    status: str,
    diff: Optional[str] = None
):
    await agent_messages_collection.update_one(
        {
            "project_id": ObjectId(project_id),
            "content": content,
            "role": "agent",
        },
        {
            "$set": {
                "status": status,
                "diff": diff,
                "updated_at": datetime.utcnow(),
            }
        }
    )



async def get_chat_history(
    project_id: str,
    user_id: str
) -> List[dict]:
    cursor = agent_messages_collection.find(
        {
            "project_id": ObjectId(project_id),
            "user_id": ObjectId(user_id)
        }
    ).sort("created_at", 1)

    messages = []
    async for doc in cursor:
        messages.append({
            "role": doc["role"],
            "content": doc["content"],
            "status": doc.get("status"),
            "diff": doc.get("diff"),
            "created_at": doc["created_at"]
        })

    return messages
async def get_recent_chat_context(
    project_id: str,
    user_id: str,
    limit: int = 6
) -> list[str]:
    cursor = (
        agent_messages_collection.find(
            {
                "project_id": ObjectId(project_id),
                "user_id": ObjectId(user_id),
                "role": {"$in": ["user", "agent"]},
            }
        )
        .sort("created_at", -1)
        .limit(limit)
    )

    messages = []
    async for doc in cursor:
        role = "User" if doc["role"] == "user" else "Agent"

        # Prefer readable message over raw_response
        content = doc.get("message") or doc.get("content")
        if not content:
            continue

        messages.append(f"{role}: {content}")

    return list(reversed(messages))
