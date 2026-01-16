CHAT_MEMORY = {}

def add_message(project_id: str, role: str, content: str):
    CHAT_MEMORY.setdefault(project_id, []).append({
        "role": role,
        "content": content
    })

def get_history(project_id: str):
    return CHAT_MEMORY.get(project_id, [])
