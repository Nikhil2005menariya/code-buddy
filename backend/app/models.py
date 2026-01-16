from pydantic import BaseModel

class ChatRequest(BaseModel):
    project_id: str
    message: str


class CreateProjectRequest(BaseModel):
    repo_path: str
