import os
import chromadb
from typing import List, Optional

from app.config import CHROMA_BASE_DIR
from app.agent.llm import get_llm
from app.agent.file_tools import (
    read_file,
    write_file,
    file_exists
)
from app.agent.diff_utils import generate_diff
from app.agent.reindex import reindex_project


SYSTEM_PROMPT = """
You are a senior software engineer acting as a coding assistant.

You are working on an existing codebase.

STRICT RULES (MUST FOLLOW EXACTLY):
- You may ONLY modify existing files.
- You MUST NOT create new files.
- You MUST NOT modify multiple files in one response.
- You MUST NOT apply changes yourself.

CRITICAL OUTPUT RULES:
- When providing NEW_CONTENT, output RAW FILE CONTENT ONLY.
- DO NOT wrap code in Markdown.
- DO NOT use ``` or ```javascript or ```ts or ```py.
- DO NOT use '''.
- DO NOT add explanations, comments, or text outside the required format.
- The NEW_CONTENT must be exactly what should be written to disk, byte-for-byte.

If a required file does NOT exist:
- DO NOT propose code changes.
- INSTEAD explain clearly:
  1) The exact file path(s) to create
  2) The full content of each file
  3) What imports/exports must be added
  4) Where the new file should be wired

WHEN MODIFYING CODE, YOU MUST FOLLOW THIS FORMAT EXACTLY:

ACTION: modify_file
PATH: <absolute file path>
DESCRIPTION: <short explanation>
NEW_CONTENT:
<full updated file content>

If no code modification is needed, respond with a normal explanation.
"""

def _extract_explicit_file_paths(question: str, repo_root: str) -> set[str]:
    """
    Detect file paths explicitly mentioned in user input
    and resolve them to absolute paths.
    """
    paths = set()
    tokens = question.replace(",", " ").split()

    for token in tokens:
        if token.endswith((".js", ".ts", ".py")):
            abs_path = os.path.join(repo_root, token)
            if file_exists(abs_path):
                paths.add(abs_path)

    return paths


def ask_repo(
    question: str,
    project_id: str,
    repo_path: str,
    chat_history: Optional[List[dict]] = None
):
    """
    Hybrid retrieval:
    1. Vector search (Chroma)
    2. Explicit file inclusion
    3. Recent chat history grounding
    """
    chroma_path = os.path.join(CHROMA_BASE_DIR, project_id)

    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection("repo")

    results = collection.query(
        query_texts=[question],
        n_results=6
    )

    context_blocks: list[str] = []
    included_paths: set[str] = set()

    # 1️⃣ Semantic retrieval
    for doc, meta in zip(
        results["documents"][0],
        results["metadatas"][0]
    ):
        path = meta.get("path")
        if path and path not in included_paths:
            context_blocks.append(f"FILE: {path}\n{doc}")
            included_paths.add(path)

    # 2️⃣ Explicit file path inclusion
    explicit_paths = _extract_explicit_file_paths(question, repo_path)
    for path in explicit_paths:
        if path not in included_paths:
            context_blocks.append(f"FILE: {path}\n{read_file(path)}")
            included_paths.add(path)

    # 3️⃣ Recent chat context (lightweight, critical for follow-ups)
    history_block = ""
    if chat_history:
        formatted = []

        for msg in chat_history:
            # Handle dict-based history (correct case)
            if isinstance(msg, dict):
                role = msg.get("role", "user").upper()
                content = msg.get("content") or msg.get("message") or ""
            # Handle string-based history (fallback safety)
            else:
                role = "USER"
                content = str(msg)

            if content:
                formatted.append(f"{role}: {content}")

        history_block = "\n".join(formatted)


    prompt = f"""
{SYSTEM_PROMPT}

Recent conversation:
{history_block}

Code context:
{chr(10).join(context_blocks)}

User request:
{question}
"""

    llm = get_llm()
    response = llm.invoke(prompt)

    return response.content


async def apply_agent_response(
    response: str,
    project_id: str,
    repo_path: str
):
    """
    Apply a single-file modification proposed by the agent.
    """
    response = response.strip()

    if not response.startswith("ACTION:"):
        return {
            "type": "explanation",
            "message": response
        }

    lines = response.splitlines()

    action = lines[0].replace("ACTION:", "").strip()
    if action != "modify_file":
        return {
            "error": "unsupported_action",
            "message": f"Unsupported action: {action}"
        }

    try:
        path_line = next(l for l in lines if l.startswith("PATH:"))
        path = path_line.replace("PATH:", "").strip()
    except StopIteration:
        raise ValueError("PATH not found in agent response")

    try:
        new_content_index = lines.index("NEW_CONTENT:") + 1
    except ValueError:
        raise ValueError("NEW_CONTENT marker missing")

    new_content = "\n".join(lines[new_content_index:]).strip()

    if not file_exists(path):
        return {
            "error": "file_missing",
            "path": path,
            "message": "File does not exist. Please create it manually."
        }

    original = read_file(path)
    diff = generate_diff(original, new_content, path)

    # Apply change
    write_file(path, new_content)

    # Reindex after modification
    await reindex_project(project_id, repo_path)

    return {
        "status": "applied",
        "path": path,
        "diff": diff
    }
