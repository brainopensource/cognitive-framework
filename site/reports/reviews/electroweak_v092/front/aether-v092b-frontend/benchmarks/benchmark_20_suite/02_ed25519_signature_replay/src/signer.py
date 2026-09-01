import hashlib
import json
import time
from cryptography.hazmat.primitives.asymmetric import ed25519

class OperatorSigner:
    def __init__(self, private_key: ed25519.Ed25519PrivateKey):
        self._private_key = private_key
        self.public_key = private_key.public_key()

    def sign_approval(self, payload: dict, nonce: str, timestamp: float) -> bytes:
        doc = {
            "payload": payload,
            "nonce": nonce,
            "timestamp": timestamp
        }
        raw = json.dumps(doc, sort_keys=True).encode("utf-8")
        return self._private_key.sign(raw)
