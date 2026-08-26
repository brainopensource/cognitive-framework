"""Deterministic in-memory EnvironmentAdapter fake.

Owning contract: ICD §4 EnvironmentAdapter, REQ-PORT-003, VG-03 §7.1.
Invariants:
- No ambient I/O, network, or clock.
- Strict path containment: zero path-escape / traversal allowed.
- Test commands are argv arrays of strings, never shell strings (slice-findings.md).
- Preview includes new files, modified files, deleted files, and diff.
- Complete rollback / compensation support.
"""

from __future__ import annotations

import os
import re
from typing import Any, Callable, Mapping, Optional, Sequence

from ...domain.canonicalisation.digest import digest_bytes, digest_of
from ...ports.environment import (
    AffectedResource,
    EffectPreview,
    EffectReceipt,
    EffectRequest,
    EnvironmentProfile,
    EnvironmentSnapshot,
    Observation,
    ObservationRequest,
    Reconciliation,
)
from ...ports.event_store import Result

__all__ = ["FakeEnvironment"]

_DIFF_HEADER = re.compile(r"^diff --git a/(.+) b/(.+)$")
_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def _is_safe_relative_path(path: str) -> bool:
    """Validate that path does not escape workspace root via .. or leading /."""
    if not path or path.startswith("/") or path.startswith("\\"):
        return False
    norm = os.path.normpath(path).replace("\\", "/")
    if norm == ".." or norm.startswith("../") or "/../" in norm:
        return False
    if norm.startswith("/"):
        return False
    return True


def _compute_file_digest(content: str) -> str:
    """Digest of text file content."""
    return digest_bytes(content.encode("utf-8"))


class FakeEnvironment:
    """Deterministic in-memory versioned environment adapter."""

    def __init__(
        self,
        initial_files: Optional[Mapping[str, str]] = None,
        environment_id: str = "fake-env-1",
        root: str = "/workspace",
        test_runner: Optional[Callable[[Sequence[str], str], tuple[int, str]]] = None,
    ) -> None:
        self._environment_id = environment_id
        self._root = root
        self._files: dict[str, str] = dict(initial_files or {})
        self._test_runner = test_runner
        self._disposed = False
        self._snapshot_seq = 0
        self._history: list[dict[str, str]] = []

    def _check_disposed(self) -> Optional[Result[Any]]:
        if self._disposed:
            return Result.fail("invalid_request", "environment adapter has been disposed")
        return None

    def profile(self) -> Result[EnvironmentProfile]:
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err
        return Result.success(
            EnvironmentProfile(
                environment_id=self._environment_id,
                kind="memory",
                root=self._root,
                capabilities=("observe", "preview", "apply", "reconcile", "compensate", "dispose"),
                properties={"file_count": len(self._files), "read_only": False},
            )
        )

    def snapshot(self) -> Result[EnvironmentSnapshot]:
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err
        self._snapshot_seq += 1
        sorted_entries = sorted(self._files.items())
        snapshot_digest = digest_of({"files": sorted_entries, "seq": self._snapshot_seq})
        return Result.success(
            EnvironmentSnapshot(
                snapshot_id=f"snap-{self._snapshot_seq:04d}",
                digest=snapshot_digest,
                created_at="2026-08-15T00:00:00.000Z",
                metadata={"file_count": len(self._files)},
            )
        )

    def observe(self, req: ObservationRequest, grant: Optional[Any] = None) -> Result[Observation]:
        del grant
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err

        action = req.action
        if action == "read":
            path = req.path or req.args.get("path")
            if not isinstance(path, str):
                return Result.fail("invalid_request", "observe 'read' requires a path string")
            if not _is_safe_relative_path(path):
                return Result.fail("denied", f"path traversal escape denied: {path!r}")
            norm_path = os.path.normpath(path).replace("\\", "/")
            if norm_path not in self._files:
                return Result.fail("not_found", f"file not found: {norm_path}")
            content = self._files[norm_path]
            return Result.success(
                Observation(
                    action="read",
                    content=content,
                    files=(norm_path,),
                    metadata={"bytes": len(content.encode("utf-8")), "digest": _compute_file_digest(content)},
                )
            )

        if action in ("search", "grep"):
            pattern = req.pattern or req.args.get("pattern", "")
            if not isinstance(pattern, str):
                return Result.fail("invalid_request", "search requires a pattern string")
            matches: list[dict[str, Any]] = []
            matching_files: list[str] = []
            for p, text in sorted(self._files.items()):
                lines = text.splitlines()
                for line_no, line in enumerate(lines, start=1):
                    if pattern in line:
                        matches.append({"file": p, "line": line_no, "content": line})
                        if p not in matching_files:
                            matching_files.append(p)
            return Result.success(
                Observation(
                    action=action,
                    matches=tuple(matches),
                    files=tuple(matching_files),
                    metadata={"total_matches": len(matches)},
                )
            )

        if action in ("list", "glob"):
            pattern = req.pattern or req.args.get("pattern", "*")
            import fnmatch
            matching_files = [
                p for p in sorted(self._files.keys())
                if fnmatch.fnmatch(p, pattern) or pattern in ("*", "")
            ]
            return Result.success(
                Observation(
                    action=action,
                    files=tuple(matching_files),
                    metadata={"total_files": len(matching_files)},
                )
            )

        if action == "stat":
            path = req.path or req.args.get("path")
            if not isinstance(path, str) or not _is_safe_relative_path(path):
                return Result.fail("denied", f"invalid or unsafe path for stat: {path!r}")
            norm_path = os.path.normpath(path).replace("\\", "/")
            if norm_path not in self._files:
                return Result.fail("not_found", f"file not found: {norm_path}")
            content = self._files[norm_path]
            return Result.success(
                Observation(
                    action="stat",
                    files=(norm_path,),
                    metadata={
                        "exists": True,
                        "bytes": len(content.encode("utf-8")),
                        "lines": len(content.splitlines()),
                        "digest": _compute_file_digest(content),
                    },
                )
            )

        return Result.fail("invalid_request", f"unsupported observation action: {action!r}")

    def _parse_and_simulate_patch(
        self, patch_text: str
    ) -> Result[tuple[dict[str, str | None], list[AffectedResource], list[str], list[str], list[str], str]]:
        """Parse unified diff and simulate on current in-memory files.

        Returns:
            (planned_files_map, affected_resources, new_files, modified_files, deleted_files, normalized_diff)
        """
        if not patch_text or not patch_text.strip():
            return Result.fail("invalid_request", "empty patch")

        lines = patch_text.splitlines()
        i = 0
        planned_files: dict[str, str | None] = {}
        affected_resources: list[AffectedResource] = []
        new_files: list[str] = []
        modified_files: list[str] = []
        deleted_files: list[str] = []

        while i < len(lines):
            line = lines[i]
            if line.startswith("diff --git "):
                i += 1
                continue
            if line.startswith("--- "):
                old_header = line[4:].strip()
                i += 1
                if i >= len(lines) or not lines[i].startswith("+++ "):
                    return Result.fail("invalid_request", "patch missing +++ header after ---")
                new_header = lines[i][4:].strip()
                i += 1

                # Clean headers
                old_path = old_header.removeprefix("a/").split("\t")[0].strip()
                new_path = new_header.removeprefix("b/").split("\t")[0].strip()

                is_new = old_header == "/dev/null" or old_path == "/dev/null"
                is_delete = new_header == "/dev/null" or new_path == "/dev/null"

                target_path = new_path if not is_delete else old_path
                if not _is_safe_relative_path(target_path):
                    return Result.fail("denied", f"path traversal escape in patch header: {target_path!r}")

                target_path = os.path.normpath(target_path).replace("\\", "/")

                # Collect hunks for this file
                old_content = self._files.get(target_path)
                if is_new:
                    if target_path in self._files:
                        pass  # overwriting existing
                    orig_lines: list[str] = []
                    pre_digest = None
                else:
                    if old_content is None:
                        return Result.fail("not_found", f"target file for patch does not exist: {target_path}")
                    orig_lines = old_content.splitlines(keepends=True)
                    pre_digest = _compute_file_digest(old_content)

                # Process hunks
                new_file_lines: list[str] = []
                orig_idx = 0
                has_hunk = False

                while i < len(lines) and lines[i].startswith("@@"):
                    has_hunk = True
                    hunk_match = _HUNK_HEADER.match(lines[i])
                    hint = None
                    if hunk_match:
                        hint = max(int(hunk_match.group(1)) - 1, 0)
                    elif lines[i].strip() not in ("@@", "@@@"):
                        return Result.fail("invalid_request", f"malformed hunk header: {lines[i]}")
                    i += 1

                    body: list[str] = []
                    while i < len(lines) and not lines[i].startswith("@@") and not lines[i].startswith("--- ") and not lines[i].startswith("diff --git"):
                        hline = lines[i]
                        i += 1
                        if hline[:1] in ("+", "-", " ", "\\"):
                            body.append(hline)
                        else:
                            i -= 1
                            break

                    expected_old = [line[1:] for line in body if line[:1] in ("-", " ")]
                    if hint is None and expected_old:
                        candidates = [
                            at for at in range(orig_idx, len(orig_lines) - len(expected_old) + 1)
                            if all(orig_lines[at + n].rstrip("\r\n") == want.rstrip("\r\n")
                                   for n, want in enumerate(expected_old))
                        ]
                        if not candidates:
                            return Result.fail("conflict", f"patch context not found in {target_path}")
                        hint = candidates[0]
                    if hint is not None:
                        if hint < orig_idx or hint > len(orig_lines):
                            return Result.fail("conflict", f"hunk starts past end of {target_path}")
                        new_file_lines.extend(orig_lines[orig_idx:hint])
                        orig_idx = hint

                    for hline in body:
                        if hline.startswith("+"):
                            new_file_lines.append(hline[1:] + "\n")
                        elif hline.startswith("-"):
                            # deletion line: check match against original
                            expected_del = hline[1:]
                            if orig_idx < len(orig_lines):
                                actual = orig_lines[orig_idx].rstrip("\r\n")
                                if actual != expected_del.rstrip("\r\n"):
                                    return Result.fail("conflict", f"patch deletion mismatch in {target_path}: expected {expected_del!r}, got {actual!r}")
                                orig_idx += 1
                            else:
                                return Result.fail("conflict", f"patch deletion extends past end of {target_path}")
                        elif hline.startswith(" "):
                            # context line
                            expected_ctx = hline[1:]
                            if orig_idx < len(orig_lines):
                                actual = orig_lines[orig_idx].rstrip("\r\n")
                                if actual != expected_ctx.rstrip("\r\n"):
                                    return Result.fail("conflict", f"patch context mismatch in {target_path}: expected {expected_ctx!r}, got {actual!r}")
                                new_file_lines.append(orig_lines[orig_idx])
                                orig_idx += 1
                            else:
                                return Result.fail("conflict", f"patch context extends past end of {target_path}")
                        elif hline.startswith("\\"):
                            # \ No newline at end of file
                            continue
                        else:
                            return Result.fail("invalid_request", f"malformed hunk line: {hline}")

                if not has_hunk and not is_delete:
                    return Result.fail("invalid_request", f"patch file {target_path} contained no hunks")

                # Copy remaining original lines
                while orig_idx < len(orig_lines):
                    new_file_lines.append(orig_lines[orig_idx])
                    orig_idx += 1

                if is_delete:
                    planned_files[target_path] = None
                    deleted_files.append(target_path)
                    affected_resources.append(
                        AffectedResource(
                            resource=target_path,
                            change="deleted",
                            pre_digest=pre_digest,
                            post_digest=None,
                        )
                    )
                elif is_new or target_path not in self._files:
                    post_content = "".join(new_file_lines)
                    planned_files[target_path] = post_content
                    new_files.append(target_path)
                    affected_resources.append(
                        AffectedResource(
                            resource=target_path,
                            change="created",
                            pre_digest=None,
                            post_digest=_compute_file_digest(post_content),
                        )
                    )
                else:
                    post_content = "".join(new_file_lines)
                    planned_files[target_path] = post_content
                    modified_files.append(target_path)
                    affected_resources.append(
                        AffectedResource(
                            resource=target_path,
                            change="modified",
                            pre_digest=pre_digest,
                            post_digest=_compute_file_digest(post_content),
                        )
                    )
            else:
                # Skip non-diff lines
                i += 1

        if not affected_resources:
            return Result.fail("invalid_request", "patch contained no actionable file changes")

        return Result.success(
            (planned_files, affected_resources, new_files, modified_files, deleted_files, patch_text)
        )

    def preview(self, req: EffectRequest, grant: Optional[Any] = None) -> Result[EffectPreview]:
        del grant
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err

        action = req.action
        if action == "patch" or req.patch is not None:
            patch_content = req.patch or req.args.get("patch", "")
            if not isinstance(patch_content, str):
                return Result.fail("invalid_request", "patch preview requires patch text")
            sim_res = self._parse_and_simulate_patch(patch_content)
            if not sim_res.ok or sim_res.value is None:
                return Result.fail(
                    kind=sim_res.error.kind if sim_res.error else "invalid_request",
                    message=sim_res.error.message if sim_res.error else "patch preview failed",
                )
            _, affected, new_f, mod_f, del_f, diff_txt = sim_res.value
            return Result.success(
                EffectPreview(
                    diff=diff_txt,
                    affected_resources=tuple(affected),
                    new_files=tuple(new_f),
                    modified_files=tuple(mod_f),
                    deleted_files=tuple(del_f),
                    stat={
                        "new_count": len(new_f),
                        "modified_count": len(mod_f),
                        "deleted_count": len(del_f),
                        "total_affected": len(affected),
                    },
                )
            )

        if action == "write":
            path = req.args.get("path")
            content = req.args.get("content", "")
            if not isinstance(path, str):
                return Result.fail("invalid_request", "write effect requires a path string")
            if not _is_safe_relative_path(path):
                return Result.fail("denied", f"path traversal escape denied: {path!r}")
            norm_path = os.path.normpath(path).replace("\\", "/")
            is_new = norm_path not in self._files
            old_content = self._files.get(norm_path)
            pre_digest = _compute_file_digest(old_content) if old_content is not None else None
            post_digest = _compute_file_digest(content)

            affected = [
                AffectedResource(
                    resource=norm_path,
                    change="created" if is_new else "modified",
                    pre_digest=pre_digest,
                    post_digest=post_digest,
                )
            ]
            new_f = [norm_path] if is_new else []
            mod_f = [norm_path] if not is_new else []
            diff = f"+++ b/{norm_path}\n@@ -0,0 +1 @@\n+{content}" if is_new else f"--- a/{norm_path}\n+++ b/{norm_path}\n"
            return Result.success(
                EffectPreview(
                    diff=diff,
                    affected_resources=tuple(affected),
                    new_files=tuple(new_f),
                    modified_files=tuple(mod_f),
                    deleted_files=(),
                    stat={"new_count": len(new_f), "modified_count": len(mod_f)},
                )
            )

        if action in ("test", "exec"):
            # Enforce argv array invariant (slice-findings.md)
            cmd = req.command if req.command is not None else req.args.get("command")
            if cmd is None or isinstance(cmd, str) or not isinstance(cmd, (list, tuple)) or not all(isinstance(x, str) for x in cmd):
                return Result.fail(
                    "invalid_request",
                    "test/exec command must be an argv array of strings, never a shell string",
                )
            if not cmd:
                return Result.fail("invalid_request", "command argv array must not be empty")
            return Result.success(
                EffectPreview(
                    diff="",
                    affected_resources=(),
                    new_files=(),
                    modified_files=(),
                    deleted_files=(),
                    stat={"command": list(cmd)},
                )
            )

        return Result.fail("invalid_request", f"unsupported effect preview action: {action!r}")

    def apply(self, req: EffectRequest, grant: Optional[Any] = None) -> Result[EffectReceipt]:
        del grant
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err

        # Save snapshot for potential rollback/compensation
        self._history.append(dict(self._files))
        observed_at = "2026-08-15T00:00:00.000Z"
        descriptor_digest = digest_of({"verb": req.verb, "action": req.action, "args": req.args})

        action = req.action
        if action == "patch" or req.patch is not None:
            patch_content = req.patch or req.args.get("patch", "")
            if not isinstance(patch_content, str):
                return Result.fail("invalid_request", "patch apply requires patch text")
            sim_res = self._parse_and_simulate_patch(patch_content)
            if not sim_res.ok or sim_res.value is None:
                return Result.fail(
                    kind=sim_res.error.kind if sim_res.error else "invalid_request",
                    message=sim_res.error.message if sim_res.error else "patch apply failed",
                )
            planned_files, affected, _, _, _, diff_txt = sim_res.value
            for target_path, content in planned_files.items():
                if content is None:
                    self._files.pop(target_path, None)
                else:
                    self._files[target_path] = content

            result_digest = digest_of({"affected": [a.resource for a in affected], "diff": diff_txt})
            return Result.success(
                EffectReceipt(
                    descriptor_digest=descriptor_digest,
                    outcome="ok",
                    observed_at=observed_at,
                    result_digest=result_digest,
                    affected_resources=tuple(affected),
                    diff=diff_txt,
                )
            )

        if action == "write":
            path = req.args.get("path")
            content = req.args.get("content", "")
            if not isinstance(path, str):
                return Result.fail("invalid_request", "write effect requires a path string")
            if not _is_safe_relative_path(path):
                return Result.fail("denied", f"path traversal escape denied: {path!r}")
            norm_path = os.path.normpath(path).replace("\\", "/")
            is_new = norm_path not in self._files
            old_content = self._files.get(norm_path)
            pre_digest = _compute_file_digest(old_content) if old_content is not None else None
            post_digest = _compute_file_digest(content)

            self._files[norm_path] = content
            affected = [
                AffectedResource(
                    resource=norm_path,
                    change="created" if is_new else "modified",
                    pre_digest=pre_digest,
                    post_digest=post_digest,
                )
            ]
            result_digest = digest_of({"resource": norm_path, "post_digest": post_digest})
            return Result.success(
                EffectReceipt(
                    descriptor_digest=descriptor_digest,
                    outcome="ok",
                    observed_at=observed_at,
                    result_digest=result_digest,
                    affected_resources=tuple(affected),
                )
            )

        if action in ("test", "exec"):
            cmd = req.command if req.command is not None else req.args.get("command")
            if cmd is None or isinstance(cmd, str) or not isinstance(cmd, (list, tuple)) or not all(isinstance(x, str) for x in cmd):
                return Result.fail(
                    "invalid_request",
                    "test/exec command must be an argv array of strings, never a shell string",
                )
            if not cmd:
                return Result.fail("invalid_request", "command argv array must not be empty")

            if self._test_runner:
                exit_code, output = self._test_runner(cmd, self._root)
            else:
                # Default deterministic fake test execution
                if any("fail" in str(arg).lower() for arg in cmd):
                    exit_code, output = 1, "FAIL: test failed in fake environment"
                else:
                    exit_code, output = 0, "PASS: 1 test passed in fake environment"

            outcome = "ok" if exit_code == 0 else "failed"
            result_digest = digest_of({"command": list(cmd), "exit_code": exit_code, "output": output})
            return Result.success(
                EffectReceipt(
                    descriptor_digest=descriptor_digest,
                    outcome=outcome,
                    observed_at=observed_at,
                    result_digest=result_digest,
                    affected_resources=(),
                    exit_code=exit_code,
                    output=output,
                )
            )

        return Result.fail("invalid_request", f"unsupported effect apply action: {action!r}")

    def reconcile(self, receipt: EffectReceipt, grant: Optional[Any] = None) -> Result[Reconciliation]:
        del grant
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err

        for res in receipt.affected_resources:
            current_content = self._files.get(res.resource)
            if res.change == "deleted":
                if current_content is not None:
                    return Result.success(
                        Reconciliation(
                            matched=False,
                            current_digest=_compute_file_digest(current_content),
                            expected_digest="null",
                            divergence=f"resource {res.resource} was expected to be deleted but exists",
                        )
                    )
            else:
                if current_content is None:
                    return Result.success(
                        Reconciliation(
                            matched=False,
                            current_digest="null",
                            expected_digest=res.post_digest or "",
                            divergence=f"resource {res.resource} missing from environment",
                        )
                    )
                current_digest = _compute_file_digest(current_content)
                if res.post_digest and current_digest != res.post_digest:
                    return Result.success(
                        Reconciliation(
                            matched=False,
                            current_digest=current_digest,
                            expected_digest=res.post_digest,
                            divergence=f"resource {res.resource} digest mismatch",
                        )
                    )

        return Result.success(
            Reconciliation(
                matched=True,
                current_digest=receipt.result_digest,
                expected_digest=receipt.result_digest,
            )
        )

    def compensate(self, receipt: EffectReceipt, grant: Optional[Any] = None) -> Result[EffectReceipt]:
        del grant
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err

        reverted_resources: list[AffectedResource] = []
        if self._history:
            prev_files = self._history.pop()
            self._files = prev_files
            for res in receipt.affected_resources:
                reverted_resources.append(
                    AffectedResource(
                        resource=res.resource,
                        change="modified",
                        pre_digest=res.post_digest,
                        post_digest=res.pre_digest,
                    )
                )
        else:
            # Revert resource by resource
            for res in receipt.affected_resources:
                if res.change == "created":
                    self._files.pop(res.resource, None)
                    reverted_resources.append(
                        AffectedResource(resource=res.resource, change="deleted", pre_digest=res.post_digest, post_digest=None)
                    )

        return Result.success(
            EffectReceipt(
                descriptor_digest=receipt.descriptor_digest,
                outcome="ok",
                observed_at="2026-08-15T00:00:00.000Z",
                result_digest=digest_of({"compensated": [r.resource for r in reverted_resources]}),
                affected_resources=tuple(reverted_resources),
            )
        )

    def dispose(self) -> Result[None]:
        self._files.clear()
        self._history.clear()
        self._disposed = True
        return Result.success(None)
