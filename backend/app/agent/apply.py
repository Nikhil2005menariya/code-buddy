from app.agent.file_tools import read_file, write_file, file_exists
from app.agent.diff_utils import generate_diff
from app.agent.reindex import reindex_project

def apply_agent_response(response: str, project_id: str):
    response = response.strip()

    if not response.startswith("ACTION:"):
        return "No valid agent action found."

    lines = response.splitlines()

    action = lines[0].replace("ACTION:", "").strip()
    if action != "modify_file":
        return f"Unsupported action: {action}"

    path = next(l for l in lines if l.startswith("PATH:")).replace("PATH:", "").strip()

    new_content_index = lines.index("NEW_CONTENT:") + 1
    new_content = "\n".join(lines[new_content_index:]).strip()

    if not file_exists(path):
        return {
            "error": "file_missing",
            "path": path,
            "message": "File does not exist. Please create it manually."
        }

    original = read_file(path)
    diff = generate_diff(original, new_content, path)

    write_file(path, new_content)
    reindex_project(project_id)

    return {
        "status": "applied",
        "diff": diff
    }
