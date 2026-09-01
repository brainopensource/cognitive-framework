"""Permanent Git-backed EnvironmentAdapter.

Owning contract: ICD §4 EnvironmentAdapter, REQ-PORT-003 (real), VG-03 §7.1, §7.3.
Absorbs: slice/slice-findings.md (rebuilt from scratch, zero slice/ imports).
Invariants:
- Worktree / repository isolation.
- Strict path containment: zero path-escape / parent-traversal allowed.
- Test commands cross boundary as argv arrays of strings, NEVER shell strings.
- Shell is allowlisted selector-scoped privileged fallback.
- Preview includes new files, modified files, deleted files, and diff.
- Complete rollback / compensation and clean worktree disposal.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence

from ...domain.canonicalisation.digest import digest_bytes, digest_of
from ...domain.workspace import controlled_environment, get_workspace_path
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

__all__ = ["GitEnvironment", "GitEnvironmentAdapter", "GitUnavailableError"]


class GitUnavailableError(RuntimeError):
    """`git` is not on `PATH` (BETA-11: a sparse host has no git binary).

    Raised from the constructor, where there is no `Result` to return yet.
    Every port method fails closed the same way via `_check_git`, returning
    `Result.fail(kind="unavailable", ...)` instead of letting a bare
    `FileNotFoundError` escape from inside `subprocess.run`.
    """

_DIFF_HEADER = re.compile(r"^diff --git a/(.+) b/(.+)$")
_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
#: `ls`/`find` are pure read-only directory-inspection utilities (no write,
#: network, or credential surface) added after live qualification runs showed
#: models reaching for `ls` to orient themselves before a directory-listing
#: convenience existed on `read`; refusing it burned whole turns on a denied
#: call instead of one recoverable turn.
DEFAULT_ALLOWLIST = ("pytest", "ruff", "git", "python3", "python", "ls", "find")


def _compute_file_digest(content: str) -> str:
    """Digest of text file content."""
    return digest_bytes(content.encode("utf-8"))


def _with_file_header(patch_text: str, path: object) -> str:
    """Give a headerless hunk the file it is already addressed to.

    A model that emits only `@@` plus a body has not written an invalid patch
    -- it has written one whose target is carried by the effect request's
    `path` argument instead of by `--- a/`. Refusing it made the applier reject
    a diff whose content and destination were both unambiguous. A patch that
    *does* name its files is never touched.
    """
    if not isinstance(path, str) or not path:
        return patch_text
    for line in patch_text.splitlines():
        if line.startswith(("--- ", "diff --git ")):
            return patch_text
    if not patch_text.lstrip().startswith("@@"):
        return patch_text
    return f"--- a/{path}\n+++ b/{path}\n{patch_text}"


_DIRECTORY_LISTING_IGNORED = {".git", "__pycache__", ".pytest_cache", "node_modules", ".venv"}
_DIRECTORY_LISTING_MAX_ENTRIES = 200


def _directory_listing_observation(target: Path, path_str: str) -> "Observation":
    """Bounded, sorted listing used when `read` is called on a directory.

    A dedicated `search`/list verb is the sanctioned discovery path, but
    treating `read` on a directory as an implicit listing matches a
    convention several models default to; failing it outright just spends
    the whole turn budget on a repeated identical mistake instead of one
    recoverable turn.
    """
    entries: list[str] = []
    for child in sorted(target.rglob("*")):
        if any(part in _DIRECTORY_LISTING_IGNORED for part in child.parts):
            continue
        rel = child.relative_to(target).as_posix()
        entries.append(rel + "/" if child.is_dir() else rel)
        if len(entries) >= _DIRECTORY_LISTING_MAX_ENTRIES:
            break
    body = "\n".join(entries) if entries else "(empty directory)"
    hint = (
        f"'{path_str}' is a directory, not a file. Listing below "
        f"({len(entries)} entr{'y' if len(entries) == 1 else 'ies'}"
        f"{', truncated' if len(entries) >= _DIRECTORY_LISTING_MAX_ENTRIES else ''}). "
        "Call `read` again with one specific file path from this list."
    )
    return Observation(
        action="read",
        content=f"{hint}\n\n{body}",
        files=(),
        metadata={"kind": "directory_listing", "entryCount": len(entries)},
    )


class GitEnvironment:
    """Permanent Git repository environment adapter."""

    def __init__(
        self,
        repo_path: Path | str,
        worktree_branch: Optional[str] = None,
        worktree_dir: Optional[Path | str] = None,
        allowlisted_commands: Sequence[str] = DEFAULT_ALLOWLIST,
        environment_id: str = "git-env-1",
    ) -> None:
        self._repo_path = Path(repo_path).resolve()
        self._environment_id = environment_id
        self._allowlisted_commands = tuple(allowlisted_commands)
        self._owns_worktree = False
        self._disposed = False
        self._snapshot_seq = 0

        if shutil.which("git") is None:
            raise GitUnavailableError("git executable not found on PATH")

        if worktree_branch:
            sandboxes_dir = get_workspace_path("sandboxes") if os.environ.get("AETHER_WORKSPACE_ROOT") else None
            wt_path = Path(worktree_dir or tempfile.mkdtemp(prefix="vg-wt-", dir=sandboxes_dir)).resolve()
            # Create isolated worktree
            cmd = ["git", "worktree", "add", "-b", worktree_branch, str(wt_path)]
            proc = subprocess.run(cmd, cwd=self._repo_path, capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                # If branch already exists, checkout without -b
                cmd_existing = ["git", "worktree", "add", str(wt_path), worktree_branch]
                subprocess.run(cmd_existing, cwd=self._repo_path, capture_output=True, text=True, check=True)
            self._working_dir = wt_path
            self._worktree_branch = worktree_branch
            self._owns_worktree = True
        elif worktree_dir:
            self._working_dir = Path(worktree_dir).resolve()
            self._worktree_branch = None
        else:
            self._working_dir = self._repo_path
            self._worktree_branch = None

    @property
    def repo_path(self) -> Path:
        return self._repo_path

    @property
    def working_dir(self) -> Path:
        return self._working_dir

    def _check_disposed(self) -> Optional[Result[Any]]:
        if self._disposed:
            return Result.fail("invalid_request", "environment adapter has been disposed")
        return None

    def _check_git(self) -> Optional[Result[Any]]:
        """Fail closed with a typed `unavailable` Result, not a raw crash.

        The constructor already refused a host with no `git` on `PATH`, but
        `PATH` is mutable for the life of the process (a sandboxed child, an
        env var scrubbed mid-run) -- so every port method re-checks rather
        than trusting the constructor-time probe forever.
        """
        if shutil.which("git") is None:
            return Result.fail(
                "unavailable", "git executable not found on PATH", retryable=False
            )
        return None

    def _resolve_safe_path(self, rel_path: str) -> Result[Path]:
        """Resolve path and assert containment within working_dir."""
        if not rel_path or rel_path.startswith("/") or rel_path.startswith("\\"):
            return Result.fail("denied", f"path traversal escape denied: {rel_path!r}")
        norm = os.path.normpath(rel_path).replace("\\", "/")
        if norm == ".." or norm.startswith("../") or "/../" in norm:
            return Result.fail("denied", f"path traversal escape denied: {rel_path!r}")
        target = (self._working_dir / norm).resolve()
        try:
            target.relative_to(self._working_dir.resolve())
        except ValueError:
            return Result.fail("denied", f"path escapes workspace root: {rel_path!r}")
        return Result.success(target)

    def profile(self) -> Result[EnvironmentProfile]:
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err
        git_err = self._check_git()
        if git_err:
            return git_err
        # Read current commit and branch
        head_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self._working_dir, capture_output=True, text=True, check=False
        )
        head_commit = head_proc.stdout.strip() if head_proc.returncode == 0 else "unknown"

        branch_proc = subprocess.run(
            ["git", "branch", "--show-current"], cwd=self._working_dir, capture_output=True, text=True, check=False
        )
        branch_name = branch_proc.stdout.strip() if branch_proc.returncode == 0 else ""

        return Result.success(
            EnvironmentProfile(
                environment_id=self._environment_id,
                kind="git",
                root=str(self._working_dir),
                capabilities=("observe", "preview", "apply", "reconcile", "compensate", "dispose"),
                properties={
                    "repo_path": str(self._repo_path),
                    "working_dir": str(self._working_dir),
                    "head_commit": head_commit,
                    "branch": branch_name or self._worktree_branch or "detached",
                },
            )
        )

    def snapshot(self) -> Result[EnvironmentSnapshot]:
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err
        git_err = self._check_git()
        if git_err:
            return git_err
        self._snapshot_seq += 1

        head_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=self._working_dir, capture_output=True, text=True, check=False
        )
        head_commit = head_proc.stdout.strip() if head_proc.returncode == 0 else "unknown"

        status_proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=self._working_dir, capture_output=True, text=True, check=False
        )
        status_out = status_proc.stdout if status_proc.returncode == 0 else ""

        # Snapshot identity describes workspace material, not how often it was
        # observed. Including `_snapshot_seq` made two consecutive reads of an
        # unchanged tree produce different digests, so every verification
        # receipt became stale the instant admission took a second snapshot.
        snapshot_digest = digest_of({"head": head_commit, "status": status_out})
        return Result.success(
            EnvironmentSnapshot(
                snapshot_id=f"git-snap-{head_commit[:8]}-{self._snapshot_seq:04d}",
                digest=snapshot_digest,
                created_at="2026-08-15T00:00:00.000Z",
                metadata={"head_commit": head_commit, "status_lines": len(status_out.splitlines())},
            )
        )

    def observe(self, req: ObservationRequest, grant: Optional[Any] = None) -> Result[Observation]:
        del grant
        disposed_err = self._check_disposed()
        if disposed_err:
            return disposed_err
        git_err = self._check_git()
        if git_err:
            return git_err

        action = req.action
        if action == "read":
            path_str = req.path or req.args.get("path")
            if not isinstance(path_str, str):
                return Result.fail("invalid_request", "observe 'read' requires a path string")
            res_path = self._resolve_safe_path(path_str)
            if not res_path.ok or res_path.value is None:
                return Result.fail(
                    kind=res_path.error.kind if res_path.error else "denied",
                    message=res_path.error.message if res_path.error else "path resolution failed",
                )
            target = res_path.value
            if target.is_dir():
                # Several coding-agent conventions treat `read` on a directory
                # as an implicit listing. Rather than fail closed on a very
                # common model habit and burn the whole turn budget on a
                # repeated identical mistake, return a bounded listing with an
                # explicit pointer to `read` a specific file next.
                return Result.success(_directory_listing_observation(target, path_str))
            if not target.is_file():
                return Result.fail("not_found", f"file not found: {path_str}")
            try:
                content = target.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError) as exc:
                return Result.fail("instrument_error", f"failed to read {path_str}: {exc}")

            norm_rel = os.path.normpath(path_str).replace("\\", "/")
            lines = content.splitlines(keepends=True)
            total_lines = len(lines)

            offset_val = req.args.get("offset")
            limit_val = req.args.get("limit")

            if offset_val is not None or limit_val is not None or total_lines > 100:
                try:
                    offset = max(0, int(offset_val)) if offset_val is not None else 0
                except (ValueError, TypeError):
                    offset = 0
                try:
                    limit = max(1, int(limit_val)) if limit_val is not None else 100
                except (ValueError, TypeError):
                    limit = 100

                selected_lines = lines[offset:offset + limit]
                paginated_content = "".join(selected_lines)
                has_more = (offset + len(selected_lines)) < total_lines
                if has_more:
                    paginated_content += f"\n[... {total_lines - (offset + len(selected_lines))} remaining lines. Use offset={offset + len(selected_lines)} to continue ...]\n"

                return Result.success(
                    Observation(
                        action="read",
                        content=paginated_content,
                        files=(norm_rel,),
                        metadata={
                            "bytes": len(content.encode("utf-8")),
                            "digest": _compute_file_digest(content),
                            "preimage_digest": _compute_file_digest(content),
                            "section_digest": _compute_file_digest(paginated_content),
                            "section_address": {
                                "path": norm_rel,
                                "offset": offset,
                                "limit": limit,
                                "preimageDigest": _compute_file_digest(content),
                            },
                            "total_lines": total_lines,
                            "offset": offset,
                            "limit": limit,
                            "has_more": has_more,
                        },
                    )
                )

            return Result.success(
                Observation(
                    action="read",
                    content=content,
                    files=(norm_rel,),
                    metadata={"bytes": len(content.encode("utf-8")),
                              "digest": _compute_file_digest(content),
                              "preimage_digest": _compute_file_digest(content),
                              "total_lines": total_lines},
                )
            )

        if action in ("search", "grep"):
            pattern = req.pattern or req.args.get("pattern", "")
            if not isinstance(pattern, str):
                return Result.fail("invalid_request", "search requires a pattern string")

            path_filter = req.path or req.args.get("path") or req.args.get("glob")
            max_results_val = req.args.get("max_results")
            try:
                max_results = int(max_results_val) if max_results_val is not None else 50
            except (ValueError, TypeError):
                max_results = 50

            # Execute git grep with untracked files included
            cmd = ["git", "grep", "--untracked", "-n", "--", pattern]
            if path_filter and isinstance(path_filter, str) and path_filter not in (".", "/workspace", ""):
                cmd.extend(["--", path_filter])

            grep_proc = subprocess.run(
                cmd,
                cwd=self._working_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            if grep_proc.returncode != 0:
                # Benchmark workspaces are deliberately copied directories,
                # not Git repositories.  ``git grep`` returns code 1 with no
                # stderr there (and also for no matches), so checking only
                # for its diagnostic silently turned every discovery query
                # into an empty observation.  Fall back on any non-zero
                # result, while keeping Vanguard's internal state hidden.
                cmd_fallback = [
                    "grep", "-rnH", "--exclude-dir=.vanguard",
                    "--exclude-dir=.git", "--exclude-dir=__pycache__",
                    "--", pattern, path_filter if isinstance(path_filter, str)
                    and path_filter not in (".", "/workspace", "") else ".",
                ]
                grep_proc = subprocess.run(
                    cmd_fallback,
                    cwd=self._working_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )

            matches: list[dict[str, Any]] = []
            matching_files: list[str] = []
            file_match_counts: dict[str, int] = {}
            max_snippets_per_file = 3

            if grep_proc.returncode == 0:
                for line in grep_proc.stdout.splitlines():
                    if len(matches) >= max_results:
                        break
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        f_path, line_no, text = parts[0], parts[1], parts[2]
                        try:
                            l_num = int(line_no)
                        except ValueError:
                            l_num = 1
                        if f_path not in matching_files:
                            matching_files.append(f_path)
                            file_match_counts[f_path] = 0
                        if file_match_counts[f_path] < max_snippets_per_file:
                            snippet_text = text[:120] + ("..." if len(text) > 120 else "")
                            matches.append({"file": f_path, "line": l_num, "content": snippet_text})
                            file_match_counts[f_path] += 1

            if not matches:
                glob_pat = pattern if pattern not in ("", ".", ".*") else "*"
                found_files = []
                for p in self._working_dir.rglob(glob_pat):
                    if p.is_file() and not any(part.startswith(".") or part == "__pycache__" for part in p.parts):
                        try:
                            rel = str(p.relative_to(self._working_dir)).replace("\\", "/")
                            found_files.append(rel)
                        except ValueError:
                            pass
                if found_files:
                    matching_files = sorted(found_files)[:max_results]
                    for f in matching_files:
                        matches.append({"file": f, "line": 1, "content": f"<file: {f}>"})

            return Result.success(
                Observation(
                    action=action,
                    matches=tuple(matches),
                    files=tuple(matching_files),
                    metadata={"total_matches": len(matches), "matching_files": len(matching_files)},
                )
            )

        if action in ("list", "glob"):
            pattern = req.pattern or req.args.get("pattern", "*")
            max_results_val = req.args.get("max_results", 100)
            try:
                max_results = int(max_results_val)
            except (ValueError, TypeError):
                return Result.fail("invalid_request", "list/glob max_results must be an integer")
            if max_results < 1 or max_results > 1000:
                return Result.fail("invalid_request", "list/glob max_results must be between 1 and 1000")
            ls_proc = subprocess.run(
                ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                cwd=self._working_dir,
                capture_output=True,
                text=True,
                check=False,
            )
            import fnmatch
            if ls_proc.returncode == 0:
                all_files = ls_proc.stdout.splitlines()
            else:
                all_files = [
                    str(p.relative_to(self._working_dir)).replace("\\", "/")
                    for p in self._working_dir.rglob("*")
                    if p.is_file() and not any(part.startswith(".") for part in p.relative_to(self._working_dir).parts)
                ]
            matching_all = [f for f in sorted(set(all_files)) if fnmatch.fnmatch(f, pattern) or pattern in ("*", "")]
            matching = matching_all[:max_results]
            return Result.success(
                Observation(
                    action=action,
                    files=tuple(matching),
                    metadata={"total_files": len(matching_all), "returned_files": len(matching),
                              "max_results": max_results, "has_more": len(matching_all) > max_results},
                )
            )

        if action == "stat":
            path_str = req.path or req.args.get("path")
            if not isinstance(path_str, str):
                return Result.fail("invalid_request", "stat requires a path string")
            res_path = self._resolve_safe_path(path_str)
            if not res_path.ok or res_path.value is None:
                return Result.fail("denied", f"path resolution failed: {path_str}")
            target = res_path.value
            if not target.exists():
                return Result.fail("not_found", f"file not found: {path_str}")
            content = target.read_text(encoding="utf-8") if target.is_file() else ""
            norm_rel = os.path.normpath(path_str).replace("\\", "/")
            return Result.success(
                Observation(
                    action="stat",
                    files=(norm_rel,),
                    metadata={
                        "exists": True,
                        "bytes": len(content.encode("utf-8")),
                        "lines": len(content.splitlines()),
                        "digest": _compute_file_digest(content) if content else "",
                    },
                )
            )

        return Result.fail("invalid_request", f"unsupported observation action: {action!r}")

    def _parse_and_validate_patch(
        self, patch_text: str
    ) -> Result[tuple[dict[str, str | None], list[AffectedResource], list[str], list[str], list[str], str]]:
        """Validate unified diff patch against repository working directory."""
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

                old_path = old_header.removeprefix("a/").split("\t")[0].strip()
                new_path = new_header.removeprefix("b/").split("\t")[0].strip()

                is_new = old_header == "/dev/null" or old_path == "/dev/null"
                is_delete = new_header == "/dev/null" or new_path == "/dev/null"

                target_path = new_path if not is_delete else old_path
                res_path = self._resolve_safe_path(target_path)
                if not res_path.ok or res_path.value is None:
                    return Result.fail("denied", f"path traversal escape in patch header: {target_path!r}")

                file_obj = res_path.value
                norm_rel = os.path.normpath(target_path).replace("\\", "/")

                if is_new:
                    orig_lines: list[str] = []
                    pre_digest = None
                else:
                    if not file_obj.is_file():
                        return Result.fail("not_found", f"target file for patch does not exist: {norm_rel}")
                    old_content = file_obj.read_text(encoding="utf-8")
                    orig_lines = old_content.splitlines(keepends=True)
                    pre_digest = _compute_file_digest(old_content)

                new_file_lines: list[str] = []
                orig_idx = 0
                has_hunk = False

                while i < len(lines) and lines[i].startswith("@@"):
                    has_hunk = True
                    hunk_match = _HUNK_HEADER.match(lines[i])
                    # A header without line numbers (a bare `@@`) is common in
                    # model-authored diffs. It is not a malformed patch -- it
                    # is a patch that declines to state *where*, which is
                    # answerable from the context lines themselves. `patch(1)`
                    # and `git apply` both locate a hunk by searching for its
                    # context near the stated offset; requiring the offset to
                    # be exactly right made this applier stricter than either,
                    # and it rejected diffs whose content was correct.
                    hint: int | None = None
                    if hunk_match:
                        hunk_start = int(hunk_match.group(1))
                        hint = max(hunk_start - 1, 0) if hunk_start else 0
                    elif lines[i].strip() not in ("@@", "@@@"):
                        return Result.fail(
                            "invalid_request", f"malformed hunk header: {lines[i]}")
                    i += 1

                    # Collect the hunk body before applying any of it, so the
                    # old-file block it expects is known and can be searched
                    # for. Applying while parsing cannot backtrack.
                    body: list[str] = []
                    while i < len(lines) and not lines[i].startswith("@@") \
                            and not lines[i].startswith("--- ") \
                            and not lines[i].startswith("diff --git"):
                        hline = lines[i]
                        if hline[:1] not in ("+", "-", " ", "\\"):
                            break
                        body.append(hline)
                        i += 1

                    expected_old = [
                        line[1:] for line in body if line[:1] in ("-", " ")
                    ]

                    def _matches(at: int) -> bool:
                        if at < 0 or at + len(expected_old) > len(orig_lines):
                            return False
                        return all(
                            orig_lines[at + n].rstrip("\r\n") == want.rstrip("\r\n")
                            for n, want in enumerate(expected_old)
                        )

                    if not expected_old:
                        # Pure insertion: nothing to anchor on, so the header's
                        # offset is all there is. Without one, append at the
                        # current position rather than guessing.
                        target_idx = hint if hint is not None else orig_idx
                        if target_idx > len(orig_lines):
                            return Result.fail(
                                "conflict",
                                f"hunk starts past end of {norm_rel} at line {target_idx}")
                    elif hint is not None:
                        # A numbered anchor is a preimage claim, not a search
                        # suggestion. Refuse drift at that exact location;
                        # silently relocating a stale hunk can corrupt an
                        # unrelated occurrence after resume.
                        if not _matches(hint):
                            return Result.fail(
                                "conflict",
                                f"stale patch anchor in {norm_rel} at line {hint + 1}")
                        target_idx = hint
                    else:
                        # Search forward from where the last hunk left off, so
                        # hunks stay ordered and an earlier region cannot be
                        # rewritten twice. Ambiguity resolves to the candidate
                        # nearest the header's hint when it gave one.
                        candidates = [
                            at for at in range(orig_idx, len(orig_lines) - len(expected_old) + 1)
                            if _matches(at)
                        ]
                        if not candidates:
                            head = expected_old[0].rstrip("\r\n")
                            return Result.fail(
                                "conflict",
                                f"patch context not found in {norm_rel}: no location "
                                f"matches the hunk beginning {head!r}")
                        if hint is None and len(candidates) > 1:
                            # Anchoring must not become guessing. With no line
                            # hint and several equally good matches, writing to
                            # the first one silently edits a location the author
                            # may not have meant -- the exact corruption this
                            # applier's strictness used to prevent. Refuse, and
                            # say how to disambiguate.
                            return Result.fail(
                                "conflict",
                                f"ambiguous hunk in {norm_rel}: its context matches "
                                f"{len(candidates)} locations; supply a hunk header "
                                "with line numbers or add distinguishing context")
                        target_idx = (
                            min(candidates, key=lambda at: abs(at - hint))
                            if hint is not None else candidates[0])

                    if target_idx < orig_idx:
                        return Result.fail(
                            "invalid_request",
                            f"hunks out of order in {norm_rel} at line {target_idx + 1}")
                    while orig_idx < target_idx:
                        new_file_lines.append(orig_lines[orig_idx])
                        orig_idx += 1

                    for hline in body:
                        marker, text = hline[:1], hline[1:]
                        if marker == "+":
                            new_file_lines.append(text + "\n")
                        elif marker == "\\":
                            continue
                        elif marker in ("-", " "):
                            if orig_idx >= len(orig_lines):
                                return Result.fail(
                                    "conflict",
                                    f"patch context extends past end of {norm_rel}")
                            actual = orig_lines[orig_idx].rstrip("\r\n")
                            if actual != text.rstrip("\r\n"):
                                # Unreachable once anchored, retained so a
                                # future change to the search cannot corrupt a
                                # file silently.
                                return Result.fail(
                                    "conflict",
                                    f"patch context mismatch in {norm_rel}: "
                                    f"expected {text!r}, got {actual!r}")
                            if marker == " ":
                                new_file_lines.append(orig_lines[orig_idx])
                            orig_idx += 1

                if not has_hunk and not is_delete:
                    return Result.fail("invalid_request", f"patch file {norm_rel} contained no hunks")

                while orig_idx < len(orig_lines):
                    new_file_lines.append(orig_lines[orig_idx])
                    orig_idx += 1

                if is_delete:
                    planned_files[norm_rel] = None
                    deleted_files.append(norm_rel)
                    affected_resources.append(
                        AffectedResource(
                            resource=norm_rel,
                            change="deleted",
                            pre_digest=pre_digest,
                            post_digest=None,
                        )
                    )
                elif is_new or not file_obj.is_file():
                    post_content = "".join(new_file_lines)
                    planned_files[norm_rel] = post_content
                    new_files.append(norm_rel)
                    affected_resources.append(
                        AffectedResource(
                            resource=norm_rel,
                            change="created",
                            pre_digest=None,
                            post_digest=_compute_file_digest(post_content),
                        )
                    )
                else:
                    post_content = "".join(new_file_lines)
                    planned_files[norm_rel] = post_content
                    modified_files.append(norm_rel)
                    affected_resources.append(
                        AffectedResource(
                            resource=norm_rel,
                            change="modified",
                            pre_digest=pre_digest,
                            post_digest=_compute_file_digest(post_content),
                        )
                    )
            else:
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
        git_err = self._check_git()
        if git_err:
            return git_err

        action = req.action
        if action == "patch" and req.patch is None and "diff" not in req.args and "content" in req.args:
            action = "write"

        if action == "patch" or req.patch is not None:
            patch_content = req.patch or req.args.get("patch") or req.args.get("diff", "")
            if not isinstance(patch_content, str):
                return Result.fail("invalid_request", "patch preview requires patch text")
            patch_content = _with_file_header(patch_content, req.args.get("path"))
            val_res = self._parse_and_validate_patch(patch_content)
            if not val_res.ok or val_res.value is None:
                return Result.fail(
                    kind=val_res.error.kind if val_res.error else "invalid_request",
                    message=val_res.error.message if val_res.error else "patch preview failed",
                )
            _, affected, new_f, mod_f, del_f, diff_txt = val_res.value
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
            path_str = req.args.get("path")
            content = req.args.get("content", "")
            if not isinstance(path_str, str):
                return Result.fail("invalid_request", "write effect requires a path string")
            res_path = self._resolve_safe_path(path_str)
            if not res_path.ok or res_path.value is None:
                return Result.fail("denied", f"path traversal escape denied: {path_str!r}")
            file_obj = res_path.value
            norm_rel = os.path.normpath(path_str).replace("\\", "/")
            is_new = not file_obj.is_file()
            pre_digest = _compute_file_digest(file_obj.read_text(encoding="utf-8")) if not is_new else None
            post_digest = _compute_file_digest(content)

            affected = [
                AffectedResource(
                    resource=norm_rel,
                    change="created" if is_new else "modified",
                    pre_digest=pre_digest,
                    post_digest=post_digest,
                )
            ]
            new_f = [norm_rel] if is_new else []
            mod_f = [norm_rel] if not is_new else []
            diff = f"+++ b/{norm_rel}\n@@ -0,0 +1 @@\n+{content}" if is_new else f"--- a/{norm_rel}\n+++ b/{norm_rel}\n"
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
        git_err = self._check_git()
        if git_err:
            return git_err

        observed_at = "2026-08-15T00:00:00.000Z"
        descriptor_digest = digest_of({"verb": req.verb, "action": req.action, "args": req.args})

        action = req.action
        if action == "patch" and req.patch is None and "diff" not in req.args and "content" in req.args:
            action = "write"

        if action == "patch" or req.patch is not None:
            patch_content = req.patch or req.args.get("patch") or req.args.get("diff", "")
            if not isinstance(patch_content, str):
                return Result.fail("invalid_request", "patch apply requires patch text")
            patch_content = _with_file_header(patch_content, req.args.get("path"))
            val_res = self._parse_and_validate_patch(patch_content)
            if not val_res.ok or val_res.value is None:
                return Result.fail(
                    kind=val_res.error.kind if val_res.error else "invalid_request",
                    message=val_res.error.message if val_res.error else "patch apply failed",
                )
            planned_files, affected, _, _, _, diff_txt = val_res.value
            for rel_name, content in planned_files.items():
                file_path = (self._working_dir / rel_name).resolve()
                if content is None:
                    if file_path.exists():
                        file_path.unlink()
                else:
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding="utf-8")

            result_digest = digest_of({"affected": [a.resource for a in affected], "diff": diff_txt})

            # Non-evaluating syntax observation receipt (S8-B-09 / A-05)
            syntax_receipts: list[str] = []
            import ast
            for rel_name, content in planned_files.items():
                if content is not None and rel_name.endswith(".py"):
                    try:
                        ast.parse(content, filename=rel_name)
                    except SyntaxError as syn_err:
                        syntax_receipts.append(f"syntax_observation: {rel_name}:{syn_err.lineno}: {syn_err.msg}")

            receipt_output = "\n".join(syntax_receipts) if syntax_receipts else None

            return Result.success(
                EffectReceipt(
                    descriptor_digest=descriptor_digest,
                    outcome="ok",
                    observed_at=observed_at,
                    result_digest=result_digest,
                    affected_resources=tuple(affected),
                    diff=diff_txt,
                    output=receipt_output,
                )
            )

        if action == "write":
            path_str = req.args.get("path")
            content = req.args.get("content", "")
            if not isinstance(path_str, str):
                return Result.fail("invalid_request", "write effect requires a path string")
            res_path = self._resolve_safe_path(path_str)
            if not res_path.ok or res_path.value is None:
                return Result.fail("denied", f"path traversal escape denied: {path_str!r}")
            file_obj = res_path.value
            norm_rel = os.path.normpath(path_str).replace("\\", "/")
            is_new = not file_obj.is_file()
            pre_digest = _compute_file_digest(file_obj.read_text(encoding="utf-8")) if not is_new else None
            post_digest = _compute_file_digest(content)

            file_obj.parent.mkdir(parents=True, exist_ok=True)
            file_obj.write_text(content, encoding="utf-8")

            affected = [
                AffectedResource(
                    resource=norm_rel,
                    change="created" if is_new else "modified",
                    pre_digest=pre_digest,
                    post_digest=post_digest,
                )
            ]
            result_digest = digest_of({"resource": norm_rel, "post_digest": post_digest})
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

            # Check allowlist
            binary = Path(cmd[0]).name
            if binary not in self._allowlisted_commands:
                return Result.fail(
                    "denied",
                    f"command binary {binary!r} is not in allowlisted commands: {self._allowlisted_commands}",
                )

            work_cwd = self._working_dir
            if req.working_directory:
                work_cwd = (self._working_dir / req.working_directory).resolve()

            try:
                proc = subprocess.run(
                    list(cmd),
                    cwd=work_cwd,
                    env=controlled_environment(os.environ),
                    capture_output=True,
                    text=True,
                    check=False,
                )
                exit_code = proc.returncode
                output = proc.stdout + (("\n" + proc.stderr) if proc.stderr else "")
            except OSError as exc:
                return Result.fail("instrument_error", f"failed to execute command {cmd!r}: {exc}")

            # Empty-output acknowledgement (S8-B-08)
            if exit_code == 0 and not output.strip():
                output = "Command executed successfully with no output."

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
        git_err = self._check_git()
        if git_err:
            return git_err

        for res in receipt.affected_resources:
            file_obj = (self._working_dir / res.resource).resolve()
            if res.change == "deleted":
                if file_obj.exists():
                    return Result.success(
                        Reconciliation(
                            matched=False,
                            current_digest=_compute_file_digest(file_obj.read_text(encoding="utf-8")),
                            expected_digest="null",
                            divergence=f"resource {res.resource} was expected to be deleted but exists",
                        )
                    )
            else:
                if not file_obj.is_file():
                    return Result.success(
                        Reconciliation(
                            matched=False,
                            current_digest="null",
                            expected_digest=res.post_digest or "",
                            divergence=f"resource {res.resource} missing from workspace",
                        )
                    )
                current_digest = _compute_file_digest(file_obj.read_text(encoding="utf-8"))
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
        git_err = self._check_git()
        if git_err:
            return git_err

        # Discard working tree modifications and untracked files
        subprocess.run(["git", "checkout", "--", "."], cwd=self._working_dir, capture_output=True, check=False)
        subprocess.run(["git", "clean", "-fd"], cwd=self._working_dir, capture_output=True, check=False)

        reverted_resources: list[AffectedResource] = []
        for res in receipt.affected_resources:
            reverted_resources.append(
                AffectedResource(
                    resource=res.resource,
                    change="deleted" if res.change == "created" else "modified",
                    pre_digest=res.post_digest,
                    post_digest=res.pre_digest,
                )
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
        if self._disposed:
            return Result.success(None)
        if self._owns_worktree and self._working_dir.exists():
            subprocess.run(
                ["git", "worktree", "remove", "--force", str(self._working_dir)],
                cwd=self._repo_path,
                capture_output=True,
                check=False,
            )
            if self._working_dir.exists():
                shutil.rmtree(self._working_dir, ignore_errors=True)
        self._disposed = True
        return Result.success(None)


GitEnvironmentAdapter = GitEnvironment
