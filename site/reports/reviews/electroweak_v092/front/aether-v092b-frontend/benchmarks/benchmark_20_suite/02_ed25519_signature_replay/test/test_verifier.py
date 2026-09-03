import unittest
import time
from cryptography.hazmat.primitives.asymmetric import ed25519
from src.signer import OperatorSigner
from src.verifier import ApprovalVerifier

class TestApprovalVerifier(unittest.TestCase):
    def setUp(self):
        self.priv_key = ed25519.Ed25519PrivateKey.generate()
        self.signer = OperatorSigner(self.priv_key)
        self.verifier = ApprovalVerifier(self.signer.public_key, max_drift_seconds=30.0)

    def test_valid_approval_accepted(self):
        now = time.time()
        payload = {"action": "deploy", "target": "prod"}
        sig = self.signer.sign_approval(payload, "nonce-1", now)
        self.assertTrue(self.verifier.verify_approval(payload, "nonce-1", now, sig, now))

    def test_expired_timestamp_rejected(self):
        now = time.time()
        old_time = now - 100.0  # 100 seconds in the past (> 30s max drift)
        payload = {"action": "transfer", "amount": 1000}
        sig = self.signer.sign_approval(payload, "nonce-old", old_time)
        self.assertFalse(
            self.verifier.verify_approval(payload, "nonce-old", old_time, sig, now),
            "FALSIFIER: Expired approval timestamp must be rejected"
        )

    def test_duplicate_nonce_rejected(self):
        now = time.time()
        payload = {"action": "delete_db"}
        sig = self.signer.sign_approval(payload, "nonce-dup", now)
        # First verification must succeed
        self.assertTrue(self.verifier.verify_approval(payload, "nonce-dup", now, sig, now))
        # Replay with same nonce must fail
        self.assertFalse(
            self.verifier.verify_approval(payload, "nonce-dup", now, sig, now + 1.0),
            "FALSIFIER: Replayed nonce must be rejected"
        )

if __name__ == "__main__":
    unittest.main()
