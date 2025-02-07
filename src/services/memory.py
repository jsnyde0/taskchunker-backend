import json
import os
import uuid

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
