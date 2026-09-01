# dispatch_engine.py - High-Level Request Pipeline
from typing import Any, Dict, Optional
from .auth import AuthManager
from .rate_governor import RateGovernor

class DispatchEngine:
    def __init__(self, auth: AuthManager, governor: RateGovernor):
        self.auth = auth
        self.governor = governor
        self.history = []

    def dispatch(self, token: str, lease_id: str, tokens: int, task: Dict[str, Any]) -> bool:
        if not self.auth.verify_scope(token, "dispatch:exec"):
            return False
        if not self.governor.reserve(lease_id, tokens):
            return False
        self.history.append({"task": task, "status": "dispatched"})
        return True
