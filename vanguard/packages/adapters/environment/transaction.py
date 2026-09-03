"""Adapter-side two-phase commit for multi-file workspace mutations.

I-7 / I-TXN: `ast.parse` lives here, never in `kernel/`. Syntax failure aborts
before any durable flush; any later commit error restores the pre-image.
"""

from __future__ import annotations

import ast
import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Sequence

from ...ports.event_store import Result

__all__ = [
    "FileMutation",
    "TransactionReceipt",
    "AtomicMultiFileTransactionManager",
    "TXN_TMP_MARKER",
]

TXN_TMP_MARKER = ".vg-txn-"


@dataclass(frozen=True, slots=True)
class FileMutation:
    path: str
    content: str | None
    action: Literal["create", "modify", "delete"]


@dataclass(frozen=True, slots=True)
class TransactionReceipt:
    transaction_id: str
    mutated_files: tuple[str, ...]
    tree_hash_before: str
    tree_hash_after: str


class AtomicMultiFileTransactionManager:
    """Two-phase commit: in-memory shadow + AST preflight, then all-or-nothing flush."""

    def __init__(self, workspace_root: Path) -> None:
        self._root = Path(workspace_root).resolve()

    def execute_transaction(
        self,
        mutations: Sequence[FileMutation],
    ) -> Result[TransactionReceipt]:
        if not mutations:
            return Result.fail("invalid_request", "transaction contained no mutations")

        resolved: list[tuple[FileMutation, Path]] = []
        for mutation in mutations:
            dest = self._resolve_safe_path(mutation.path)
            if dest is None:
                return Result.fail(
                    "denied",
                    f"path traversal escape denied: {mutation.path!r}",
                )
            resolved.append((mutation, dest))

        snapshots = self._snapshot(resolved)
        preflight = self._preflight(mutations)
        if preflight is not None:
            return preflight

        transaction_id = uuid.uuid4().hex
        tree_before = self._tree_hash(tuple(mutation.path for mutation in mutations))
        commit_err = self._commit(resolved, snapshots, transaction_id)
        if commit_err is not None:
            return commit_err

        return Result.success(
            TransactionReceipt(
                transaction_id=transaction_id,
                mutated_files=tuple(mutation.path for mutation in mutations),
                tree_hash_before=tree_before,
                tree_hash_after=self._tree_hash(tuple(mutation.path for mutation in mutations)),
            )
        )

    def _resolve_safe_path(self, rel_path: str) -> Path | None:
        if not rel_path or rel_path.startswith("/") or rel_path.startswith("\\"):
            return None
        norm = os.path.normpath(rel_path).replace("\\", "/")
        if norm == ".." or norm.startswith("../") or "/../" in norm:
            return None
        target = (self._root / norm).resolve()
        try:
            target.relative_to(self._root)
        except ValueError:
            return None
        return target

    def _snapshot(
        self,
        resolved: Sequence[tuple[FileMutation, Path]],
    ) -> dict[str, bytes | None]:
        snapshots: dict[str, bytes | None] = {}
        for mutation, dest in resolved:
            if dest.is_file():
                snapshots[mutation.path] = dest.read_bytes()
            else:
                snapshots[mutation.path] = None
        return snapshots

    def _preflight(self, mutations: Sequence[FileMutation]) -> Result[TransactionReceipt] | None:
        for mutation in mutations:
            if mutation.content is None or mutation.action == "delete":
                continue
            if not mutation.path.endswith(".py"):
                continue
            try:
                ast.parse(mutation.content, filename=mutation.path)
            except SyntaxError as syn_err:
                return Result.fail(
                    "invalid_request",
                    f"SyntaxError at {mutation.path}:{syn_err.lineno}: {syn_err.msg}",
                )
        return None

    def _commit(
        self,
        resolved: Sequence[tuple[FileMutation, Path]],
        snapshots: dict[str, bytes | None],
        transaction_id: str,
    ) -> Result[TransactionReceipt] | None:
        staged: list[Path] = []
        try:
            for mutation, dest in resolved:
                if mutation.content is None or mutation.action == "delete":
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                tmp = dest.parent / f".{dest.name}{TXN_TMP_MARKER}{transaction_id}.tmp"
                tmp.write_text(mutation.content, encoding="utf-8")
                staged.append(tmp)
            stage_index = 0
            for mutation, dest in resolved:
                if mutation.content is None or mutation.action == "delete":
                    continue
                os.replace(staged[stage_index], dest)
                stage_index += 1
            for mutation, dest in resolved:
                if mutation.content is None or mutation.action == "delete":
                    if dest.is_file():
                        dest.unlink()
        except OSError as exc:
            self._restore(snapshots)
            self._unlink_tmps(staged)
            return Result.fail("instrument_error", f"transaction commit failed: {exc}")
        self._unlink_tmps(staged)
        return None

    def _restore(self, snapshots: dict[str, bytes | None]) -> None:
        for rel_path, payload in snapshots.items():
            dest = self._root / rel_path
            if payload is None:
                if dest.is_file():
                    dest.unlink()
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(payload)

    def _unlink_tmps(self, staged: Sequence[Path]) -> None:
        for tmp in staged:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                continue

    def _tree_hash(self, paths: Sequence[str]) -> str:
        digest = hashlib.sha256()
        for rel_path in sorted(paths):
            digest.update(rel_path.encode("utf-8"))
            dest = self._root / rel_path
            if dest.is_file():
                digest.update(dest.read_bytes())
            else:
                digest.update(b"<missing>")
        return "sha256:" + digest.hexdigest()
