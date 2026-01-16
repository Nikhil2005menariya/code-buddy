from app.agent.repo_agent import ask_repo
from app.chat.pending_actions import set_pending_action

def run_agent(question: str, project_id: str, repo_path: str):
    response = ask_repo(question, project_id)

    if response.strip().startswith("ACTION:"):
        set_pending_action(project_id, {
            "raw_response": response
        })

        return {
            "type": "proposal",
            "message": "Agent proposes a code change",
            "details": response
        }

    return {
        "type": "explanation",
        "message": response
    }
