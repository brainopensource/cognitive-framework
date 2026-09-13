"""Runner-independent isolation and nonmutation meta-test (NT-B01, NT-B02, NT-B03).

Enforces:
1. Disposable repository fixtures with independent Git metadata (never shared/linked worktrees).
2. Pure content hashing (sha256) of source, index, generated knowledge, and corpora.
3. Proof that deliberate source, index, generated-knowledge, corpus, addition, and deletion
   mutations fail the nonmutation check.
4. Proof that child test environments have provider credentials removed and outbound network denied.
5. Proof that representative test execution preserves byte-identical repository state.
"""

from __future__ import annotations

import hashlib
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Mapping, Sequence
from unittest.mock import patch

from test import (
    ContainmentBlocker,
    build_hermetic_test_env,
    establish_test_environment,
    probe_bwrap_available,
    probe_bwrap_containment,
    probe_lda_index_available,
    require_bwrap,
)
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.state_contract import resolve_state_directory
from tools.linters.check_test_hygiene import (
    PROVIDER_KEYS,
    check_test_hygiene,
    detect_unsafe_inherited_state,
    exported_provider_keys,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]


def compute_file_sha256(path: Path) -> str:
    """Compute deterministic SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_tree_manifest(root: Path, subtrees: Sequence[str] | None = None) -> dict[str, str]:
    """Compute relative_path -> sha256 hex for all files in specified subtrees."""
    manifest: dict[str, str] = {}
    search_dirs: list[Path] = []

    if subtrees is None:
        search_dirs.append(root)
    else:
        for st in subtrees:
            p = root / st
            if p.is_file():
                rel = str(p.relative_to(root)).replace("\\", "/")
                manifest[rel] = compute_file_sha256(p)
            elif p.is_dir():
                search_dirs.append(p)

    for base in search_dirs:
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            rel_path = p.relative_to(root)
            if ".git" in rel_path.parts:
                continue
            rel = str(rel_path).replace("\\", "/")
            manifest[rel] = compute_file_sha256(p)

    return manifest


def compare_tree_manifests(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """Compare two tree manifests and return human-readable discrepancies."""
    diffs: list[str] = []
    before_keys = set(before.keys())
    after_keys = set(after.keys())

    # Deleted files
    for k in sorted(before_keys - after_keys):
        diffs.append(f"DELETED: {k}")

    # Added files
    for k in sorted(after_keys - before_keys):
        diffs.append(f"ADDED: {k}")

    # Modified files
    for k in sorted(before_keys & after_keys):
        if before[k] != after[k]:
            diffs.append(f"MODIFIED: {k} (before={before[k][:8]}, after={after[k][:8]})")

    return diffs


def assert_tree_nonmutation(before: dict[str, str], after: dict[str, str]) -> None:
    """Assert that before and after manifests are byte-identical, failing closed with diffs."""
    diffs = compare_tree_manifests(before, after)
    if diffs:
        formatted = "\n  ".join(diffs)
        raise AssertionError(f"Nonmutation violation detected:\n  {formatted}")


def create_disposable_repo_fixture(parent_dir: Path) -> Path:
    """Create an independently rooted disposable repository with its own Git metadata.

    The fixture repository is strictly hermetic and never touches or queries the
    shared/contributor repository metadata.
    """
    repo_dir = parent_dir / "disposable_repo"
    repo_dir.mkdir(parents=True, exist_ok=True)

    git_bin = shutil.which("git") or "/usr/bin/git"
    git_env = {
        "GIT_DIR": str(repo_dir / ".git"),
        "GIT_WORK_TREE": str(repo_dir),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(parent_dir),
    }

    # Initialize independent repository
    subprocess.run([git_bin, "init"], cwd=repo_dir, env=git_env, check=True, capture_output=True)
    subprocess.run(
        [git_bin, "config", "user.name", "Aether Disposable Fixture"],
        cwd=repo_dir,
        env=git_env,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [git_bin, "config", "user.email", "disposable@aether.local"],
        cwd=repo_dir,
        env=git_env,
        check=True,
        capture_output=True,
    )

    # Populate structure mimicking canonical layout
    (repo_dir / "vanguard" / "packages" / "domain").mkdir(parents=True, exist_ok=True)
    (repo_dir / ".lda").mkdir(parents=True, exist_ok=True)
    (repo_dir / ".generated" / "knowledge").mkdir(parents=True, exist_ok=True)
    (repo_dir / "tools" / "002_LLM_API_MOCK").mkdir(parents=True, exist_ok=True)
    (repo_dir / "test").mkdir(parents=True, exist_ok=True)

    # Initial file contents
    (repo_dir / "vanguard" / "packages" / "domain" / "sample.py").write_text(
        "\"\"\"Sample domain module.\"\"\"\nVALUE = 42\n", encoding="utf-8"
    )
    (repo_dir / ".lda" / "index.db").write_bytes(b"SQLite format 3\x00disposable-lda-index")
    (repo_dir / ".generated" / "knowledge" / "report.json").write_text(
        "{\"status\": \"VALIDATED\", \"counts\": {\"symbols\": 1}}\n", encoding="utf-8"
    )
    (repo_dir / "tools" / "002_LLM_API_MOCK" / "lam.sqlite").write_bytes(
        b"SQLite format 3\x00disposable-tracked-lam-db"
    )
    (repo_dir / "test" / "test_sample.py").write_text(
        "import unittest\nfrom vanguard.packages.domain.sample import VALUE\n"
        "class TestSample(unittest.TestCase):\n    def test_val(self): self.assertEqual(VALUE, 42)\n",
        encoding="utf-8",
    )
    (repo_dir / "pyproject.toml").write_text("[project]\nname = \"disposable-test\"\n", encoding="utf-8")

    # Commit initial state in disposable repository
    subprocess.run([git_bin, "add", "."], cwd=repo_dir, env=git_env, check=True, capture_output=True)
    subprocess.run(
        [git_bin, "commit", "-m", "initial disposable commit"],
        cwd=repo_dir,
        env=git_env,
        check=True,
        capture_output=True,
    )

    return repo_dir


def compute_git_metadata_manifest(repo: Path) -> dict[str, str]:
    """Compute sha256 manifest of essential Git metadata (HEAD, index, refs)."""
    git_dir = repo / ".git"
    manifest: dict[str, str] = {}
    if not git_dir.is_dir():
        return manifest

    for target in ("HEAD", "index"):
        p = git_dir / target
        if p.is_file():
            manifest[f".git/{target}"] = compute_file_sha256(p)

    refs_dir = git_dir / "refs"
    if refs_dir.is_dir():
        for p in refs_dir.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(repo)).replace("\\", "/")
                manifest[rel] = compute_file_sha256(p)

    return manifest


def compute_full_candidate_manifest(repo: Path, include_git: bool = True) -> dict[str, str]:
    """Compute sha256 manifest of candidate source, index, generated knowledge, corpus, and Git metadata."""
    subtrees = ("vanguard", ".lda", ".generated", "tools/002_LLM_API_MOCK")
    manifest = compute_tree_manifest(repo, subtrees)
    if include_git:
        git_manifest = compute_git_metadata_manifest(repo)
        manifest.update(git_manifest)
    return manifest


def create_disposable_candidate_subject(parent_dir: Path) -> Path:
    """Create a disposable copy of the actual candidate subject with its own Git metadata.

    Copies candidate source lattice (vanguard/), LDA index (.lda/), generated knowledge (.generated/),
    tracked mock corpus (tools/002_LLM_API_MOCK/), pyproject.toml, and representative tests (test/).
    Initializes an independent, hermetic Git repository so operations never touch or share host Git state.
    """
    repo_dir = parent_dir / "candidate_subject"
    repo_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy candidate subject components
    shutil.copytree(
        _REPO_ROOT / "vanguard",
        repo_dir / "vanguard",
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "dist", "node_modules"),
    )
    if (_REPO_ROOT / ".lda").is_dir():
        shutil.copytree(
            _REPO_ROOT / ".lda",
            repo_dir / ".lda",
            ignore=shutil.ignore_patterns("*.tmp"),
        )
    if (_REPO_ROOT / ".generated").is_dir():
        shutil.copytree(
            _REPO_ROOT / ".generated",
            repo_dir / ".generated",
        )
    if (_REPO_ROOT / "tools" / "002_LLM_API_MOCK").is_dir():
        shutil.copytree(
            _REPO_ROOT / "tools" / "002_LLM_API_MOCK",
            repo_dir / "tools" / "002_LLM_API_MOCK",
        )
    if (_REPO_ROOT / "pyproject.toml").is_file():
        shutil.copy2(_REPO_ROOT / "pyproject.toml", repo_dir / "pyproject.toml")

    # Copy representative tests
    test_dst = repo_dir / "test"
    test_dst.mkdir(parents=True, exist_ok=True)
    if (_REPO_ROOT / "test" / "kernel").is_dir():
        shutil.copytree(
            _REPO_ROOT / "test" / "kernel",
            test_dst / "kernel",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    if (_REPO_ROOT / "test" / "__init__.py").is_file():
        shutil.copy2(_REPO_ROOT / "test" / "__init__.py", test_dst / "__init__.py")
    if (_REPO_ROOT / "test" / "conftest.py").is_file():
        shutil.copy2(_REPO_ROOT / "test" / "conftest.py", test_dst / "conftest.py")

    # 2. Initialize independent git repository
    git_bin = shutil.which("git") or "/usr/bin/git"
    git_env = {
        "GIT_DIR": str(repo_dir / ".git"),
        "GIT_WORK_TREE": str(repo_dir),
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(parent_dir),
    }
    subprocess.run([git_bin, "init"], cwd=repo_dir, env=git_env, check=True, capture_output=True)
    subprocess.run(
        [git_bin, "config", "user.name", "Aether Candidate Fixture"],
        cwd=repo_dir,
        env=git_env,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        [git_bin, "config", "user.email", "candidate@aether.local"],
        cwd=repo_dir,
        env=git_env,
        check=True,
        capture_output=True,
    )
    subprocess.run([git_bin, "add", "."], cwd=repo_dir, env=git_env, check=True, capture_output=True)
    subprocess.run(
        [git_bin, "commit", "-m", "initial candidate snapshot"],
        cwd=repo_dir,
        env=git_env,
        check=True,
        capture_output=True,
    )

    return repo_dir


class TestDisposableRepositoryIsolation(unittest.TestCase):
    """Test that the disposable fixture resolves inside independent repository metadata (NT-B02)."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory(prefix="aether_nonmutation_")
        self.tmp_path = Path(self._temp_dir.name)
        self.repo = create_disposable_repo_fixture(self.tmp_path)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_disposable_repo_has_independent_git_metadata(self) -> None:
        """The disposable repository must have its own .git and never touch shared Git metadata."""
        git_dir = self.repo / ".git"
        self.assertTrue(git_dir.is_dir(), "Disposable repo must contain its own .git directory")

        git_bin = shutil.which("git") or "/usr/bin/git"
        git_env = {
            "GIT_DIR": str(git_dir),
            "GIT_WORK_TREE": str(self.repo),
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.tmp_path),
        }
        res = subprocess.run(
            [git_bin, "rev-parse", "--git-dir"],
            cwd=self.repo,
            env=git_env,
            capture_output=True,
            text=True,
            check=True,
        )
        resolved_git_dir = Path(res.stdout.strip()).resolve()
        self.assertEqual(resolved_git_dir, git_dir.resolve())
        self.assertNotEqual(
            resolved_git_dir,
            (_REPO_ROOT / ".git").resolve(),
            "Disposable fixture must never resolve to host repository .git",
        )

    def test_disposable_repo_structure_matches_canonical(self) -> None:
        """Verify all tracked categories exist in the disposable fixture."""
        self.assertTrue((self.repo / "vanguard" / "packages" / "domain" / "sample.py").is_file())
        self.assertTrue((self.repo / ".lda" / "index.db").is_file())
        self.assertTrue((self.repo / ".generated" / "knowledge" / "report.json").is_file())
        self.assertTrue((self.repo / "tools" / "002_LLM_API_MOCK" / "lam.sqlite").is_file())

    def test_candidate_subject_has_independent_git_metadata_and_canonical_files(self) -> None:
        """The candidate subject fixture contains actual trees and independent Git metadata."""
        candidate_repo = create_disposable_candidate_subject(self.tmp_path)
        git_dir = candidate_repo / ".git"
        self.assertTrue(git_dir.is_dir())
        self.assertTrue((candidate_repo / "vanguard" / "packages" / "kernel").is_dir())
        self.assertTrue((candidate_repo / ".lda" / "index.db").is_file())
        self.assertTrue((candidate_repo / ".generated" / "knowledge" / "report.json").is_file())
        self.assertTrue((candidate_repo / "tools" / "002_LLM_API_MOCK" / "lam.sqlite").is_file())

        git_bin = shutil.which("git") or "/usr/bin/git"
        git_env = {
            "GIT_DIR": str(git_dir),
            "GIT_WORK_TREE": str(candidate_repo),
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": str(self.tmp_path),
        }
        res = subprocess.run(
            [git_bin, "rev-parse", "--git-dir"],
            cwd=candidate_repo,
            env=git_env,
            capture_output=True,
            text=True,
            check=True,
        )
        resolved_git_dir = Path(res.stdout.strip()).resolve()
        self.assertEqual(resolved_git_dir, git_dir.resolve())
        self.assertNotEqual(
            resolved_git_dir,
            (_REPO_ROOT / ".git").resolve(),
        )


class TestContentHashingAndNonmutation(unittest.TestCase):
    """Test content hashing (sha256) and detection of deliberate mutations (NT-B02)."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory(prefix="aether_nonmutation_")
        self.tmp_path = Path(self._temp_dir.name)
        self.repo = create_disposable_repo_fixture(self.tmp_path)
        self.subtrees = ("vanguard", ".lda", ".generated", "tools/002_LLM_API_MOCK")
        self.baseline = compute_tree_manifest(self.repo, self.subtrees)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_hashing_is_deterministic_and_clean_matches(self) -> None:
        """Identical files produce identical digests and zero manifest diffs."""
        recomputed = compute_tree_manifest(self.repo, self.subtrees)
        self.assertEqual(self.baseline, recomputed)
        assert_tree_nonmutation(self.baseline, recomputed)

    def test_injected_source_mutation_detected(self) -> None:
        """Deliberate source file mutation must be detected and fail closed."""
        source_file = self.repo / "vanguard" / "packages" / "domain" / "sample.py"
        with open(source_file, "a", encoding="utf-8") as f:
            f.write("# DELIBERATE MUTATION INJECTION\n")

        mutated = compute_tree_manifest(self.repo, self.subtrees)
        diffs = compare_tree_manifests(self.baseline, mutated)
        self.assertEqual(len(diffs), 1)
        self.assertTrue(diffs[0].startswith("MODIFIED: vanguard/packages/domain/sample.py"))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(self.baseline, mutated)

    def test_injected_index_mutation_detected(self) -> None:
        """Deliberate LDA index mutation must be detected and fail closed."""
        index_file = self.repo / ".lda" / "index.db"
        with open(index_file, "ab") as f:
            f.write(b"\xde\xad\xbe\xef")

        mutated = compute_tree_manifest(self.repo, self.subtrees)
        diffs = compare_tree_manifests(self.baseline, mutated)
        self.assertEqual(len(diffs), 1)
        self.assertTrue(diffs[0].startswith("MODIFIED: .lda/index.db"))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(self.baseline, mutated)

    def test_injected_generated_knowledge_mutation_detected(self) -> None:
        """Deliberate generated knowledge mutation must be detected and fail closed."""
        report_file = self.repo / ".generated" / "knowledge" / "report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("{\"status\": \"MUTATED\"}\n")

        mutated = compute_tree_manifest(self.repo, self.subtrees)
        diffs = compare_tree_manifests(self.baseline, mutated)
        self.assertEqual(len(diffs), 1)
        self.assertTrue(diffs[0].startswith("MODIFIED: .generated/knowledge/report.json"))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(self.baseline, mutated)

    def test_injected_corpus_mutation_detected(self) -> None:
        """Deliberate LAM mock corpus mutation must be detected and fail closed."""
        corpus_file = self.repo / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"
        with open(corpus_file, "ab") as f:
            f.write(b"\xca\xfe\xba\xbe")

        mutated = compute_tree_manifest(self.repo, self.subtrees)
        diffs = compare_tree_manifests(self.baseline, mutated)
        self.assertEqual(len(diffs), 1)
        self.assertTrue(diffs[0].startswith("MODIFIED: tools/002_LLM_API_MOCK/lam.sqlite"))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(self.baseline, mutated)

    def test_injected_file_addition_detected(self) -> None:
        """Deliberate file addition / staging leak in source tree must be detected."""
        leak_file = self.repo / "vanguard" / "packages" / "leaked_artifact.pyc"
        leak_file.write_bytes(b"\x00\x01\x02")

        mutated = compute_tree_manifest(self.repo, self.subtrees)
        diffs = compare_tree_manifests(self.baseline, mutated)
        self.assertTrue(any("ADDED: vanguard/packages/leaked_artifact.pyc" in d for d in diffs))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(self.baseline, mutated)

    def test_injected_file_deletion_detected(self) -> None:
        """Deliberate file deletion must be detected and fail closed."""
        target_file = self.repo / "vanguard" / "packages" / "domain" / "sample.py"
        target_file.unlink()

        mutated = compute_tree_manifest(self.repo, self.subtrees)
        diffs = compare_tree_manifests(self.baseline, mutated)
        self.assertTrue(any("DELETED: vanguard/packages/domain/sample.py" in d for d in diffs))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(self.baseline, mutated)

    def test_injected_git_metadata_mutation_detected(self) -> None:
        """Deliberate Git metadata mutation must be detected and fail closed."""
        baseline_with_git = compute_full_candidate_manifest(self.repo, include_git=True)
        git_head = self.repo / ".git" / "HEAD"
        with open(git_head, "a", encoding="utf-8") as f:
            f.write("# MUTATED HEAD\n")

        mutated = compute_full_candidate_manifest(self.repo, include_git=True)
        diffs = compare_tree_manifests(baseline_with_git, mutated)
        self.assertTrue(any(".git/HEAD" in d for d in diffs))
        with self.assertRaises(AssertionError):
            assert_tree_nonmutation(baseline_with_git, mutated)


class TestChildEnvironmentHermeticity(unittest.TestCase):
    """Prove child test environments have credentials removed and network access denied (NT-B02)."""

    def test_subprocess_credentials_removed_probe(self) -> None:
        """A child subprocess probe demonstrates provider credentials are absent."""
        dirty_env = {
            "OPENROUTER_API_KEY": "sk-test-live-1",
            "DEEPSEEK_API_KEY": "sk-test-live-2",
            "OPENAI_API_KEY": "sk-test-live-3",
            "ANTHROPIC_API_KEY": "sk-test-live-4",
            "CUSTOM_API_KEY": "sk-test-live-5",
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        }
        hermetic_env = build_hermetic_test_env(base_env=dirty_env)

        probe_code = (
            "import os, sys\n"
            "from tools.linters.check_test_hygiene import exported_provider_keys\n"
            "leaked = exported_provider_keys()\n"
            "if leaked:\n"
            "    print(f\"LEAK: {leaked}\", file=sys.stderr)\n"
            "    sys.exit(1)\n"
            "sys.exit(0)\n"
        )
        res = subprocess.run(
            [sys.executable, "-c", probe_code],
            env=hermetic_env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0, f"Probe failed with credentials present: {res.stderr}")

    def test_subprocess_network_denied_probe(self) -> None:
        """A child subprocess probe demonstrates outbound network is denied, fail-closed."""
        hermetic_env = build_hermetic_test_env()

        # Probe attempts outbound network communication
        probe_code = (
            "import socket, sys, urllib.request\n"
            "# 1. Test proxy/HTTP denial\n"
            "try:\n"
            "    urllib.request.urlopen(\"http://1.1.1.1\", timeout=0.5)\n"
            "    print(\"FAIL: HTTP request succeeded through denied proxy\", file=sys.stderr)\n"
            "    sys.exit(2)\n"
            "except Exception:\n"
            "    pass\n"
            "sys.exit(0)\n"
        )
        res = subprocess.run(
            [sys.executable, "-c", probe_code],
            env=hermetic_env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0, f"Network probe failed: {res.stderr}")

        # If bwrap is available, verify unshared network namespace denies raw sockets
        if probe_bwrap_available():
            bwrap = shutil.which("bwrap")
            bwrap_probe = (
                "import socket, sys\n"
                "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
                "s.settimeout(0.5)\n"
                "try:\n"
                "    s.connect((\"1.1.1.1\", 80))\n"
                "    print(\"FAIL: raw socket connected in unshared net namespace\", file=sys.stderr)\n"
                "    sys.exit(3)\n"
                "except OSError:\n"
                "    sys.exit(0)\n"
            )
            res_bwrap = subprocess.run(
                [
                    bwrap,
                    "--unshare-all",
                    "--unshare-user",
                    "--ro-bind", "/", "/",
                    "--",
                    sys.executable,
                    "-c",
                    bwrap_probe,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_bwrap.returncode, 0, f"Bwrap network unshare failed: {res_bwrap.stderr}")

    def test_probe_fails_closed_if_credential_injected(self) -> None:
        """Verify the probe actually fails when a credential is present."""
        bad_env = dict(os.environ)
        bad_env["OPENROUTER_API_KEY"] = "sk-unfiltered"

        probe_code = (
            "import os, sys\n"
            "from tools.linters.check_test_hygiene import exported_provider_keys\n"
            "leaked = exported_provider_keys()\n"
            "sys.exit(1 if leaked else 0)\n"
        )
        res = subprocess.run(
            [sys.executable, "-c", probe_code],
            env=bad_env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(res.returncode, 0, "Probe must exit nonzero when credentials leak")


class TestRepresentativeExecutionNonmutation(unittest.TestCase):
    """Prove that representative test execution preserves byte-identical repository state."""

    def test_representative_execution_in_disposable_candidate_subject(self) -> None:
        """Representative test execution inside disposable candidate subject preserves all file digests (NT-B02)."""
        with tempfile.TemporaryDirectory(prefix="aether_cand_") as tmp:
            tmp_path = Path(tmp)
            repo = create_disposable_candidate_subject(tmp_path)
            before = compute_full_candidate_manifest(repo, include_git=True)

            # Establish disposable workspace outside the candidate repo
            ws_root = tmp_path / "disposable_ws"
            env = build_hermetic_test_env(workspace_root=ws_root)
            env["PYTHONPATH"] = str(repo)

            # Execute representative test within candidate repo
            res = subprocess.run(
                [sys.executable, "-m", "unittest", "test.kernel.test_grant_wire_shape"],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, f"Candidate test execution failed: {res.stderr}")

            after = compute_full_candidate_manifest(repo, include_git=True)
            assert_tree_nonmutation(before, after)

    def test_contributor_tracked_corpus_indexes_and_git_metadata_unmutated(self) -> None:
        """Check contributor repo tracked corpus, index, generated knowledge, and Git metadata are unmutated."""
        files_to_watch: list[Path] = []
        tracked_lam = _REPO_ROOT / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"
        if tracked_lam.is_file():
            files_to_watch.append(tracked_lam)
        lda_db = _REPO_ROOT / ".lda" / "index.db"
        if lda_db.is_file():
            files_to_watch.append(lda_db)
        report_json = _REPO_ROOT / ".generated" / "knowledge" / "report.json"
        if report_json.is_file():
            files_to_watch.append(report_json)

        # Track contributor Git metadata
        git_dir = _REPO_ROOT / ".git"
        if (git_dir / "HEAD").is_file():
            files_to_watch.append(git_dir / "HEAD")
        if (git_dir / "index").is_file():
            files_to_watch.append(git_dir / "index")
        refs_dir = git_dir / "refs"
        if refs_dir.is_dir():
            for p in refs_dir.rglob("*"):
                if p.is_file():
                    files_to_watch.append(p)

        before_digests = {str(f): compute_file_sha256(f) for f in files_to_watch}

        # Run representative focused test suite
        res = subprocess.run(
            [sys.executable, "-m", "unittest", "test.tools.test_check_test_hygiene"],
            cwd=_REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 0, f"Test suite run failed: {res.stderr}")

        after_digests = {str(f): compute_file_sha256(f) for f in files_to_watch}
        self.assertEqual(
            before_digests,
            after_digests,
            "Tracked contributor files or Git metadata mutated during test execution!",
        )


class TestWritableStateRedirection(unittest.TestCase):
    """Test that all writable state paths are redirected to disposable locations (NT-B02)."""

    def test_all_writable_paths_redirected_to_disposable(self) -> None:
        """Verify that temporary, cache, and runtime directories point to disposable paths."""
        with tempfile.TemporaryDirectory(prefix="aether_ws_test_") as tmp:
            ws_root = Path(tmp) / "custom_ws"
            env = establish_test_environment(workspace_root=ws_root)

            # Workspace root
            self.assertEqual(Path(env["AETHER_WORKSPACE_ROOT"]).resolve(), ws_root.resolve())

            # Temporary paths
            for var in ("TMPDIR", "TMP", "TEMP"):
                p = Path(env[var]).resolve()
                self.assertTrue(p == (ws_root / "tmp").resolve())

            # XDG paths
            self.assertEqual(Path(env["XDG_CACHE_HOME"]).resolve(), (ws_root / "cache").resolve())
            self.assertEqual(Path(env["XDG_STATE_HOME"]).resolve(), (ws_root / "state").resolve())
            self.assertEqual(Path(env["XDG_CONFIG_HOME"]).resolve(), (ws_root / "config").resolve())
            self.assertEqual(Path(env["XDG_DATA_HOME"]).resolve(), (ws_root / "data").resolve())
            self.assertEqual(Path(env["XDG_RUNTIME_DIR"]).resolve(), (ws_root / "run").resolve())

            # Caches
            self.assertEqual(
                Path(env["PYTHONPYCACHEPREFIX"]).resolve(),
                (ws_root / "cache" / "python").resolve(),
            )
            self.assertEqual(
                Path(env["npm_config_cache"]).resolve(),
                (ws_root / "cache" / "npm").resolve(),
            )

            # LAM DB copy
            tracked_lam = _REPO_ROOT / "tools" / "002_LLM_API_MOCK" / "lam.sqlite"
            redirected_lam = Path(env["LAM_DB_PATH"]).resolve()
            self.assertNotEqual(redirected_lam, tracked_lam.resolve())
            self.assertTrue(str(redirected_lam).startswith(str(ws_root.resolve())))

            # BAAC runs redirected
            self.assertEqual(Path(env["BAAC_RUNS_DIR"]).resolve(), (ws_root / "baac_runs").resolve())

            # VANGUARD_STATE_DIR must NOT be forced in the environment,
            # ensuring caller/workspace precedence is strictly preserved.
            self.assertNotIn("VANGUARD_STATE_DIR", env)


class TestStateDirectoryPrecedence(unittest.TestCase):
    """Prove default ApplicationService/CLI state-directory precedence works after importing test (NT-B01)."""

    def setUp(self) -> None:
        self._temp_dir = tempfile.TemporaryDirectory(prefix="aether_state_prec_")
        self.tmp_path = Path(self._temp_dir.name)
        self.workspace = self.tmp_path / "workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self._temp_dir.cleanup()

    def test_default_workspace_state_directory_precedence_after_test_import(self) -> None:
        """Importing test must not override default state dir resolution to workspace/.vanguard."""
        import test  # noqa: F401

        resolved = resolve_state_directory(workspace=self.workspace)
        expected = (self.workspace / ".vanguard").resolve()
        self.assertEqual(resolved.resolve(), expected)

    def test_explicit_state_dir_precedence(self) -> None:
        """Explicit state_dir takes precedence over workspace default."""
        custom_state = self.tmp_path / "custom_state"
        resolved = resolve_state_directory(workspace=self.workspace, state_dir=custom_state)
        self.assertEqual(resolved.resolve(), custom_state.resolve())

    def test_application_service_state_dir_resolution(self) -> None:
        """ApplicationService resolves state_dir to workspace/.vanguard by default."""
        svc = ApplicationService(workspace=self.workspace)
        self.assertEqual(svc.workspace.resolve(), self.workspace.resolve())
        resolved = resolve_state_directory(svc.workspace)
        self.assertEqual(resolved.resolve(), (self.workspace / ".vanguard").resolve())


class TestContainmentQualification(unittest.TestCase):
    """Test bubblewrap containment qualification and fail-closed typed blocker (NT-B03)."""

    def test_containment_blocker_is_typed_runtime_error(self) -> None:
        """ContainmentBlocker must inherit from RuntimeError, not unittest.SkipTest."""
        self.assertTrue(issubclass(ContainmentBlocker, RuntimeError))
        self.assertFalse(issubclass(ContainmentBlocker, unittest.SkipTest))

    def test_require_bwrap_raises_containment_blocker_when_unsupported(self) -> None:
        """require_bwrap must raise ContainmentBlocker if bwrap containment probe fails."""
        with patch("test.conftest.probe_bwrap_containment", return_value=(False, "mock containment failure")):
            with self.assertRaises(ContainmentBlocker) as ctx:
                require_bwrap(allow_skip=False)
            self.assertIn("mock containment failure", str(ctx.exception))

    def test_require_bwrap_allows_skip_only_when_explicit(self) -> None:
        """require_bwrap only skips when allow_skip=True is explicitly requested."""
        with patch("test.conftest.probe_bwrap_containment", return_value=(False, "mock containment failure")):
            with self.assertRaises(unittest.SkipTest):
                require_bwrap(allow_skip=True)

    def test_probe_bwrap_containment_qualifies_unshare_all(self) -> None:
        """probe_bwrap_containment qualifies unshare-all, unshare-user, and ro-bind."""
        ok, reason = probe_bwrap_containment()
        if ok:
            self.assertIsNone(reason)
            self.assertTrue(probe_bwrap_available())
        else:
            self.assertIsInstance(reason, str)
            self.assertFalse(probe_bwrap_available())
