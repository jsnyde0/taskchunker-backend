import json
import os
import uuid
from datetime import datetime
from typing import Dict, Optional

import redis

# Try to get Redis URL first (for Railway), fallback to individual params (for local)
redis_url = os.getenv("REDIS_URL")

if redis_url:
    # Parse Redis URL from Railway
    r = redis.from_url(redis_url, decode_responses=True)
else:
    # Fallback to local development settings
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_db = int(os.getenv("REDIS_DB", "0"))
    r = redis.Redis(
        host=redis_host, port=redis_port, db=redis_db, decode_responses=True
    )


def start_conversation() -> str:
    """Generate a new conversation ID and start with a blank slate."""
    conversation_id = str(uuid.uuid4())
    r.delete(conversation_id)  # Ensure there's no existing data for this ID.
    return conversation_id


def add_message(conversation_id: str, role: str, content: str) -> None:
    """Append a new message to the conversation stored in Redis."""
    message = json.dumps({"role": role, "content": content})
    r.rpush(conversation_id, message)


def get_history(conversation_id: str) -> str:
    """Retrieve the entire conversation history as a single string."""
    messages = r.lrange(conversation_id, 0, -1)
    history = []
    for msg in messages:
        try:
            m = json.loads(msg)
            # Optionally, prefix each message with its role.
            history.append(f"{m['role']}: {m['content']}")
        except Exception:
            history.append(msg)
    return "\n".join(history)


def save_task_tree(conversation_id: str, task_tree: Dict) -> None:
    """Save the task tree to Redis under the conversation."""

    # Convert datetime objects to ISO format strings
    def convert_datetimes(obj):
        if isinstance(obj, dict):
            return {k: convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_datetimes(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    task_tree_serializable = convert_datetimes(task_tree)
    task_tree_str = json.dumps(task_tree_serializable)
    key = f"task_tree:{conversation_id}"
    r.set(key, task_tree_str)


def get_task_tree(
    conversation_id: str, task_id: Optional[str] = None
) -> Optional[Dict]:
    """
    Retrieve a task tree from Redis.
    If task_id is provided, returns the subtree for that specific task.
    If task_id is None, returns the entire conversation tree.
    """
    key = f"task_tree:{conversation_id}"
    task_tree_str = r.get(key)

    if not task_tree_str:
        return None

    full_tree = json.loads(task_tree_str)

    if not task_id:
        return full_tree

    # Find specific task subtree
    task_tree = _find_task_in_tree(full_tree["tree"], task_id)
    return task_tree if task_tree else None


def _find_task_in_tree(tree: Dict, task_id: str) -> Optional[Dict]:
    """Recursively find a task in the tree by its ID."""
    if tree["task"]["id"] == task_id:
        return tree

    for subtask in tree["subtasks"]:
        result = _find_task_in_tree(subtask, task_id)
        if result:
            return result

    return None
