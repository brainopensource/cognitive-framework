# auth.py - Scope and Permission Verifier
from typing import Set, Dict, Optional

class AuthManager:
    def __init__(self):
        self._tokens: Dict[str, Set[str]] = {}

    def register_token(self, token: str, scopes: Set[str]) -> None:
        self._tokens[token] = set(scopes)

    def verify_scope(self, token: str, required_scope: str) -> bool:
        if token not in self._tokens:
            return False
        return required_scope in self._tokens[token]
