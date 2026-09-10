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

from test import (
    build_hermetic_test_env,
    establish_test_environment,
    probe_bwrap_available,
    probe_lda_index_available,
)
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

    def test_representative_execution_in_disposable_repo(self) -> None:
        """Representative test execution inside disposable repo preserves all file digests."""
        with tempfile.TemporaryDirectory(prefix="aether_rep_") as tmp:
            tmp_path = Path(tmp)
            repo = create_disposable_repo_fixture(tmp_path)
            subtrees = ("vanguard", ".lda", ".generated", "tools/002_LLM_API_MOCK")
            before = compute_tree_manifest(repo, subtrees)

            # Establish disposable workspace outside the repo
            ws_root = tmp_path / "disposable_ws"
            env = establish_test_environment(workspace_root=ws_root)
            env["PYTHONPATH"] = str(repo)

            # Execute sample test within disposable repo
            test_file = repo / "test" / "test_sample.py"
            res = subprocess.run(
                [sys.executable, "-m", "unittest", str(test_file)],
                cwd=repo,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, f"Sample test failed: {res.stderr}")

            after = compute_tree_manifest(repo, subtrees)
            assert_tree_nonmutation(before, after)

    def test_contributor_tracked_corpus_and_indexes_unmutated(self) -> None:
        """Check that contributor repo tracked LAM db and index are byte-identical after test execution."""
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
            "Tracked contributor files mutated during test execution!",
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

            # BAAC & Vanguard state
            self.assertEqual(Path(env["BAAC_RUNS_DIR"]).resolve(), (ws_root / "baac_runs").resolve())
            self.assertEqual(
                Path(env["VANGUARD_STATE_DIR"]).resolve(),
                (ws_root / "vanguard_state").resolve(),
            )
