# Greenfield PRD: Cryptographic Merkle Tree Ledger

## Objective
Implement `MerkleTree` in `src/merkle.py`.

## Requirements
- `MerkleTree()`
- `append(data: bytes) -> int`: Appends a leaf and returns leaf index.
- `get_root_hash() -> str`: Computes SHA-256 root hash of the tree. If empty, returns empty string.
- `get_proof(leaf_index: int) -> list[dict]`: Generates audit inclusion proof `[{"position": "left"|"right", "hash": str}]`.
- `verify_proof(leaf_data: bytes, leaf_index: int, proof: list[dict], root_hash: str) -> bool`: Static/class method verifying inclusion against root.
