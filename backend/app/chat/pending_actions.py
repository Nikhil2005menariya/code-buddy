PENDING_ACTIONS = {}

def set_pending_action(project_id: str, action: dict):
    PENDING_ACTIONS[project_id] = action

def get_pending_action(project_id: str):
    return PENDING_ACTIONS.get(project_id)

def clear_pending_action(project_id: str):
    if project_id in PENDING_ACTIONS:
        del PENDING_ACTIONS[project_id]
