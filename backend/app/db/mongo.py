from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017")
DB_NAME = "repo_agent"

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

users_collection = db.users
projects_collection = db.projects
chats_collection = db.chats
pending_actions_collection = db.pending_actions
agent_messages_collection = db.agent_messages
