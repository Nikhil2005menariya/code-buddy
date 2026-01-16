from fastapi import APIRouter, HTTPException
from app.db.mongo import users_collection
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)
from pydantic import BaseModel

router = APIRouter(prefix="/auth")

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(username: str, password: str):
    if await users_collection.find_one({"username": username}):
        raise HTTPException(status_code=400, detail="User already exists")

    user = {
        "username": username,
        "password": hash_password(password)
    }
    await users_collection.insert_one(user)
    return {"status": "registered"}

@router.post("/login")
async def login(data: LoginRequest):
    user = await users_collection.find_one({"username": data.username})
    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "user_id": str(user["_id"]),
        "username": user["username"]
    })

    return {"access_token": token}
