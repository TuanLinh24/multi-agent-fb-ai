import time

class SessionStore:

    def __init__(self):

        self.sessions = {}
        self.ttl = 1800

    def get_history(self, session_id):

        if session_id not in self.sessions:
            return []

        return self.sessions[session_id]["history"][-5:]

    def add_message(self, session_id, user, assistant):

        now = time.time()

        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "updated_at": now
            }

        self.sessions[session_id]["history"].append({
            "user": user,
            "assistant": assistant
        })

        self.sessions[session_id]["updated_at"] = now