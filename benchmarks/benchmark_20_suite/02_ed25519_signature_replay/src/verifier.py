import json
from typing import Set
from cryptography.hazmat.primitives.asymmetric import ed25519

class ApprovalVerifier:
    def __init__(self, public_key: ed25519.Ed25519PublicKey, max_drift_seconds: float = 60.0):
        self.public_key = public_key
        self.max_drift_seconds = max_drift_seconds
        self.seen_nonces: Set[str] = set()

    def verify_approval(self, payload: dict, nonce: str, timestamp: float, signature: bytes, current_time: float) -> bool:
        doc = {
            "payload": payload,
            "nonce": nonce,
            "timestamp": timestamp
        }
        raw = json.dumps(doc, sort_keys=True).encode("utf-8")
        try:
            self.public_key.verify(signature, raw)
        except Exception:
            return False

        # BUG: The verifier checks cryptographic validity, but completely ignores
        # timestamp freshness verification and fails to reject or record seen nonces!
        return True
