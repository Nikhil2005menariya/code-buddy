from datetime import datetime
from bson import ObjectId
from app.db.mongo import projects_collection


async def create_project(user_id: str, repo_path: str):
    project = {
        "user_id": ObjectId(user_id),
        "repo_path": repo_path,
        "status": "indexing",
        "created_at": datetime.utcnow(),
    }

    result = await projects_collection.insert_one(project)
    project["_id"] = result.inserted_id
    return project


async def get_project(project_id: str, user_id: str):
    """
    Get a project by ID that belongs to the given user
    (used by API routes for authorization).
    """
    if not ObjectId.is_valid(project_id):
        return None

    return await projects_collection.find_one(
        {
            "_id": ObjectId(project_id),
            "user_id": ObjectId(user_id),
        }
    )


async def get_project_by_id(project_id: str):
    """
    Get a project by ID without user filtering
    (used internally by chat / indexing logic).
    """
    if not ObjectId.is_valid(project_id):
        return None

    return await projects_collection.find_one(
        {"_id": ObjectId(project_id)}
    )


async def list_projects(user_id: str):
    cursor = projects_collection.find(
        {"user_id": ObjectId(user_id)}
    )
    return [project async for project in cursor]


async def update_project_status(project_id: str, status: str):
    if not ObjectId.is_valid(project_id):
        return

    await projects_collection.update_one(
        {"_id": ObjectId(project_id)},
        {"$set": {"status": status}},
    )
