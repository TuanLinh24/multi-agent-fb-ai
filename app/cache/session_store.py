import time
from collections import defaultdict

sessions = defaultdict(list)
last_updated = {}

MAX_HISTORY = 5
SESSION_TTL_SECONDS = 3600


def _cleanup():
    now = time.time()
    expired = [
        session_id
        for session_id, updated_at in last_updated.items()
        if now - updated_at > SESSION_TTL_SECONDS
    ]
    for session_id in expired:
        sessions.pop(session_id, None)
        last_updated.pop(session_id, None)


def add_message(session_id, role, content):
    _cleanup()
    sessions[session_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })
    last_updated[session_id] = time.time()

    if len(sessions[session_id]) > MAX_HISTORY:
        sessions[session_id] = sessions[session_id][-MAX_HISTORY:]


def get_history(session_id):
    _cleanup()
    return sessions[session_id]