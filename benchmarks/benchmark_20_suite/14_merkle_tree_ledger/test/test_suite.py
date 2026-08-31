import unittest
from src.merkle import MerkleTree

class TestMerkleTree(unittest.TestCase):
    def test_inclusion_proof_and_verification(self):
        tree = MerkleTree()
        idx0 = tree.append(b"event-0-init")
        idx1 = tree.append(b"event-1-action")
        idx2 = tree.append(b"event-2-commit")
        idx3 = tree.append(b"event-3-close")

        root = tree.get_root_hash()
        self.assertEqual(len(root), 64)

        proof = tree.get_proof(idx1)
        self.assertTrue(MerkleTree.verify_proof(b"event-1-action", idx1, proof, root))

        # Tampering with leaf data must fail
        self.assertFalse(MerkleTree.verify_proof(b"event-1-tampered", idx1, proof, root))

if __name__ == "__main__":
    unittest.main()
