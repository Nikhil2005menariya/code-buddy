from dotenv import load_dotenv
load_dotenv()
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.auth.api import router as auth_router
from app.projects.api import router as projects_router
from app.chat.api import router as chat_router

app = FastAPI(title="Repo Agent Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace with frontend domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(chat_router)
