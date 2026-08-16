```python
"""
Persistent Immutable AVL Tree with Structural Sharing and Snapshot Rollback.

This module provides a fully immutable AVL tree implementation where every
insertion or deletion returns a new root while reusing unchanged subtrees
(path copying). It supports range queries, snapshot management with versioning,
and rollback/branching from any prior version.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, TypeVar

K = TypeVar("K")  # key type (must be comparable)
V = TypeVar("V")  # value type


@dataclass(frozen=True)
class Node:
    """Immutable AVL tree node."""

    key: K
    value: V
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    height: int = 1

    def __repr__(self) -> str:
        return f"Node(key={self.key}, value={self.value}, height={self.height})"


# ----------------------------------------------------------------------
# AVL tree helper functions (all return new nodes, never mutate)
# ----------------------------------------------------------------------


def _height(node: Optional[Node]) -> int:
    """Return the height of a node (0 for None)."""
    return node.height if node else 0


def _balance_factor(node: Node) -> int:
    """Return balance factor of a node (left height - right height)."""
    return _height(node.left) - _height(node.right)


def _update_height(node: Node) -> Node:
    """Return a new node with corrected height (shallow copy)."""
    new_height = 1 + max(_height(node.left), _height(node.right))
    # Since Node is frozen, we need to create a new instance.
    # We use object.__setattr__ to bypass frozen for efficiency,
    # but that breaks immutability guarantees. Instead we create a new node.
    # However, we only change height, so we can use a helper.
    # For production, we could use a mutable builder, but here we keep it pure.
    return Node(
        key=node.key,
        value=node.value,
        left=node.left,
        right=node.right,
        height=new_height,
    )


def _rotate_right(y: Node) -> Node:
    """Right rotation (LL case). Returns new root."""
    x = y.left
    if x is None:
        return y  # should not happen in valid AVL
    T2 = x.right
    # Create new nodes for x and y (immutable)
    new_x = Node(
        key=x.key,
        value=x.value,
        left=x.left,
        right=y,
        height=0,  # will be updated
    )
    new_y = Node(
        key=y.key,
        value=y.value,
        left=T2,
        right=y.right,
        height=0,
    )
    # Update heights
    new_y = _update_height(new_y)
    new_x = _update_height(new_x)
    # Reassign right of new_x to new_y
    # Since we already created new_x with right=y, we need to replace it.
    # Better approach: create nodes in correct order.
    # Let's do it step by step:
    # Actually we can create new_y first, then new_x with right=new_y.
    new_y = Node(
        key=y.key,
        value=y.value,
        left=T2,
        right=y.right,
        height=0,
    )
    new_y = _update_height(new_y)
    new_x = Node(
        key=x.key,
        value=x.value,
        left=x.left,
        right=new_y,
        height=0,
    )
    new_x = _update_height(new_x)
    return new_x


def _rotate_left(x: Node) -> Node:
    """Left rotation (RR case). Returns new root."""
    y = x.right
    if y is None:
        return x
    T2 = y.left
    new_x = Node(
        key=x.key,
        value=x.value,
        left=x.left,
        right=T2,
        height=0,
    )
    new_x = _update_height(new_x)
    new_y = Node(
        key=y.key,
        value=y.value,
        left=new_x,
        right=y.right,
        height=0,
    )
    new_y = _update_height(new_y)
    return new_y


def _balance(node: Node) -> Node:
    """Balance a node after insertion/deletion. Returns new root."""
    node = _update_height(node)
    bf = _balance_factor(node)
    if bf > 1:
        # Left heavy
        if node.left and _balance_factor(node.left) < 0:
            # LR case: left-right rotation
            node = Node(
                key=node.key,
                value=node.value,
                left=_rotate_left(node.left),
                right=node.right,
                height=0,
            )
            node = _update_height(node)
        return _rotate_right(node)
    if bf < -1:
        # Right heavy
        if node.right and _balance_factor(node.right) > 0:
            # RL case: right-left rotation
            node = Node(
                key=node.key,
                value=node.value,
                left=node.left,
                right=_rotate_right(node.right),
                height=0,
            )
            node = _update_height(node)
        return _rotate_left(node)
    return node


# ----------------------------------------------------------------------
# Core operations (immutable, path copying)
# ----------------------------------------------------------------------


def insert(root: Optional[Node], key: K, value: V) -> Node:
    """Insert (key, value) into the AVL tree. Returns new root.

    If key already exists, its value is updated.
    """
    if root is None:
        return Node(key=key, value=value)
    if key < root.key:
        new_left = insert(root.left, key, value)
        new_node = Node(
            key=root.key,
            value=root.value,
            left=new_left,
            right=root.right,
            height=0,
        )
        return _balance(new_node)
    elif key > root.key:
        new_right = insert(root.right, key, value)
        new_node = Node(
            key=root.key,
            value=root.value,
            left=root.left,
            right=new_right,
            height=0,
        )
        return _balance(new_node)
    else:
        # Key exists: update value
        return Node(
            key=root.key,
            value=value,
            left=root.left,
            right=root.right,
            height=root.height,
        )


def _min_value_node(node: Node) -> Node:
    """Return the node with the smallest key in the subtree."""
    current = node
    while current.left is not None:
        current = current.left
    return current


def delete(root: Optional[Node], key: K) -> Optional[Node]:
    """Delete key from the AVL tree. Returns new root (or None if tree becomes empty).

    If key does not exist, returns the original root unchanged.
    """
    if root is None:
        return None
    if key < root.key:
        new_left = delete(root.left, key)
        if new_left is root.left:
            return root  # no change
        new_node = Node(
            key=root.key,
            value=root.value,
            left=new_left,
            right=root.right,
            height=0,
        )
        return _balance(new_node)
    elif key > root.key:
        new_right = delete(root.right, key)
        if new_right is root.right:
            return root
        new_node = Node(
            key=root.key,
            value=root.value,
            left=root.left,
            right=new_right,
            height=0,
        )
        return _balance(new_node)
    else:
        # Key found
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        # Node with two children: get inorder successor (smallest in right subtree)
        successor = _min_value_node(root.right)
        new_right = delete(root.right, successor.key)
        new_node = Node(
            key=successor.key,
            value=successor.value,
            left=root.left,
            right=new_right,
            height=0,
        )
        return _balance(new_node)


def range_query(root: Optional[Node], low: K, high: K) -> List[Tuple[K, V]]:
    """Return list of (key, value) pairs with keys in [low, high] (inclusive).

    Time: O(log N + K) where K is number of keys in range.
    """
    result: List[Tuple[K, V]] = []

    def _traverse(node: Optional[Node]) -> None:
        if node is None:
            return
        if low < node.key:
            _traverse(node.left)
        if low <= node.key <= high:
            result.append((node.key, node.value))
        if node.key < high:
            _traverse(node.right)

    _traverse(root)
    return result


# ----------------------------------------------------------------------
# Snapshot Manager
# ----------------------------------------------------------------------


class TreeHistory:
    """Manages versioned roots of a persistent AVL tree.

    Each version is identified by a user-provided ID (e.g., timestamp or string).
    Supports rollback (retrieve root of a given version) and branching
    (create a new version from an existing one).
    """

    def __init__(self) -> None:
        self._versions: Dict[Any, Optional[Node]] = {}

    def create_snapshot(self, version_id: Any, root: Optional[Node]) -> None:
        """Store a root under the given version ID."""
        self._versions[version_id] = root

    def get_root(self, version_id: Any) -> Optional[Node]:
        """Retrieve the root of a given version. Raises KeyError if not found."""
        if version_id not in self._versions:
            raise KeyError(f"Version '{version_id}' not found.")
        return self._versions[version_id]

    def rollback(self, version_id: Any) -> Optional[Node]:
        """Alias for get_root, returns root for rollback."""
        return self.get_root(version_id)

    def branch(self, version_id: Any) -> Optional[Node]:
        """Return root of a version to start a new branch (same as get_root)."""
        return self.get_root(version_id)

    def list_versions(self) -> List[Any]:
        """Return list of all stored version IDs."""
        return list(self._versions.keys())

    def __contains__(self, version_id: Any) -> bool:
        return version_id in self._versions


# ----------------------------------------------------------------------
# Unit tests (embedded)
# ----------------------------------------------------------------------


def _assert_avl_invariant(node: Optional[Node]) -> int:
    """Check AVL balance invariant and return height. Raises AssertionError."""
    if node is None:
        return 0
    left_h = _assert_avl_invariant(node.left)
    right_h = _assert_avl_invariant(node.right)
    assert abs(left_h - right_h) <= 1, f"Balance violation at key {node.key}"
    assert node.height == 1 + max(left_h, right_h), f"Height mismatch at key {node.key}"
    # BST property
    if node.left:
        assert node.left.key < node.key, f"BST violation left at {node.key}"
    if node.right:
        assert node.right.key > node.key, f"BST violation right at {node.key}"
    return node.height


def _inorder_keys(node: Optional[Node]) -> List[K]:
    """Return sorted list of keys."""
    if node is None:
        return []
    return _inorder_keys(node.left) + [node.key] + _inorder_keys(node.right)


def test_immutability():
    """Test that insert/delete return new nodes and old root is unchanged."""
    root = None
    root1 = insert(root, 10, "a")
    root2 = insert(root1, 20, "b")
    # root1 should still have only key 10
    assert _inorder_keys(root1) == [10]
    assert _inorder_keys(root2) == [10, 20]
    # delete from root2 should not affect root1
    root3 = delete(root2, 10)
    assert _inorder_keys(root1) == [10]
    assert _inorder_keys(root2) == [10, 20]
    assert _inorder_keys(root3) == [20]
    print("test_immutability passed.")


def test_avl_balance():
    """Test that AVL balance is maintained after many insertions and deletions."""
    root = None
    for key in [10, 20, 30, 40, 50, 25]:
        root = insert(root, key, str(key))
        _assert_avl_invariant(root)
    # Delete some keys
    for key in [20, 40]:
        root = delete(root, key)
        _assert_avl_invariant(root)
    # Check final keys
    assert _inorder_keys(root) == [10, 25, 30, 50]
    print("test_avl_balance passed.")


def test_range_query():
    """Test range query returns correct sorted pairs."""
    root = None
    for k, v in [(1, "a"), (3, "c"), (5, "e"), (7, "g"), (9, "i")]:
        root = insert(root, k, v)
    result = range_query(root, 3, 7)
    assert result == [(3, "c"), (5, "e"), (7, "g")]
    # Empty range
    result = range_query(root, 10, 20)
    assert result == []
    # Single key
    result = range_query(root, 5, 5)
    assert result == [(5, "e")]
    print("test_range_query passed.")


def test_duplicate_update():
    """Test that inserting existing key updates value."""
    root = insert(None, 1, "old")
    root = insert(root, 1, "new")
    assert _inorder_keys(root) == [1]
    # Retrieve value via range query
    assert range_query(root, 1, 1) == [(1, "new")]
    print("test_duplicate_update passed.")


def test_delete_nonexistent():
    """Test deleting a key that does not exist returns same tree."""
    root = insert(None, 1, "a")
    root2 = delete(root, 999)
    assert root is root2  # same object because no change
    print("test_delete_nonexistent passed.")


def test_snapshot_manager():
    """Test TreeHistory with snapshots, rollback, and branching."""
    history = TreeHistory()
    root = None
    root = insert(root, 10, "ten")
    history.create_snapshot("v1", root)
    root = insert(root, 20, "twenty")
    history.create_snapshot("v2", root)
    root = insert(root, 5, "five")
    history.create_snapshot("v3", root)

    # Rollback to v1
    v1_root = history.rollback("v1")
    assert _inorder_keys(v1_root) == [10]
    # Branch from v2
    v2_root = history.branch("v2")
    assert _inorder_keys(v2_root) == [10, 20]
    # Ensure v3 unchanged
    v3_root = history.get_root("v3")
    assert _inorder_keys(v3_root) == [5, 10, 20]
    print("test_snapshot_manager passed.")


def test_edge_cases():
    """Test empty tree, single node, and large sequence."""
    # Empty tree
    assert range_query(None, 1, 10) == []
    assert delete(None, 1) is None
    # Single node
    root = insert(None, 42, "answer")
    assert _inorder_keys(root) == [42]
    root = delete(root, 42)
    assert root is None
    # Large insertion sequence (stress balance)
    root = None
    for i in range(1000):
        root = insert(root, i, i)
        _assert_avl_invariant(root)
    for i in range(1000):
        root = delete(root, i)
        _assert_avl_invariant(root)
    assert root is None
    print("test_edge_cases passed.")


if __name__ == "__main__":
    test_immutability()
    test_avl_balance()
    test_range_query()
    test_duplicate_update()
    test_delete_nonexistent()
    test_snapshot_manager()
    test_edge_cases()
    print("\nAll tests passed.")
```