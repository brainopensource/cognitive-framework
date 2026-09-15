"""T-143 — greenfield and multi-file oracle completeness.

DIR-C7: exterior verification of the exact submitted candidate with meaningful
required-behavior coverage. Workers emit an immutable candidate reference;
this evaluator never mints acceptance or merge authority.

Lease: IsolatedEvaluator plus new falsifiers. Extends T-131 evidence identity
work; it does not duplicate product-path evidence_capture.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from vanguard.packages.adapters.evaluators.isolated import IsolatedEvaluator
from vanguard.packages.ports.evaluator import EvaluationProtocol, RunRef


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_digest(files: dict[str, Path]) -> str:
    entries = [
        f"{rel}:{hashlib.sha256(path.read_bytes()).hexdigest()}"
        for rel, path in sorted(files.items())
    ]
    return "sha256:" + hashlib.sha256("\n".join(entries).encode()).hexdigest()


class TestT143OracleCompleteness(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name)
        (self.workspace / "pkg").mkdir()
        self.a = self.workspace / "pkg" / "a.py"
        self.b = self.workspace / "pkg" / "b.py"
        self.a.write_text("def add(x, y):\n    return x + y\n", encoding="utf-8")
        self.b.write_text("def mul(x, y):\n    return x * y\n", encoding="utf-8")
        self.oracle_dir = self.workspace / "tests"
        self.oracle_dir.mkdir()
        self.oracle = self.oracle_dir / "test_oracle.py"
        self.oracle.write_text(
            "import unittest\n"
            "from pkg.a import add\n"
            "from pkg.b import mul\n"
            "\n"
            "class TestPair(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n"
            "    def test_mul(self):\n"
            "        self.assertEqual(mul(2, 3), 6)\n"
            "\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        subprocess.run(
            ["git", "add", "pkg/a.py", "pkg/b.py", "tests/test_oracle.py"],
            cwd=self.workspace, check=True,
        )
        self.required = ("pkg/a.py", "pkg/b.py")
        self.live = _tree_digest({"pkg/a.py": self.a, "pkg/b.py": self.b})
        self.protocol = EvaluationProtocol(
            name="coding-oracle@3",
            parameters={
                "candidateDigest": self.live,
                "requiredFiles": list(self.required),
                "verificationSubjectDigest": self.live,
            },
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _evaluator(self, **overrides: object) -> IsolatedEvaluator:
        options: dict[str, object] = {
            "workspace": self.workspace,
            "oracle_digests": {"tests/test_oracle.py": _digest(self.oracle)},
            "command": ("python3", "tests/test_oracle.py"),
            "expected_uid": os.getuid(),
            "image_digest": "sha256:" + "a" * 64,
            "required_files": self.required,
            "candidate_digest": self.live,
            "verification_subject_digest": self.live,
        }
        options.update(overrides)
        return IsolatedEvaluator(**options)  # type: ignore[arg-type]

    def _claim(self, evaluator: IsolatedEvaluator | None = None, protocol: EvaluationProtocol | None = None):
        result = (evaluator or self._evaluator()).evaluate(
            RunRef("t143", episode_id="ep-t143"), protocol or self.protocol)
        self.assertTrue(result.ok, result)
        return result.value

    def test_positive_multi_file_candidate_passes_and_is_not_acceptance(self) -> None:
        verdict = self._claim()
        self.assertEqual(verdict.outcome, "claims")
        claim = verdict.claims[0]
        self.assertEqual(claim["event"], "EvaluationCompleted")
        self.assertEqual(claim["status"], "passed")
        self.assertEqual(claim["candidateDigest"], self.live)
        self.assertTrue(claim["probes"]["candidateCompleteness"])
        self.assertNotIn("accepted", claim)
        self.assertNotEqual(claim["status"], "accepted")
        self.assertNotIn("merge", str(claim).lower())

    def test_empty_workspace_is_an_empty_stub(self) -> None:
        self.a.unlink()
        self.b.unlink()
        protocol = EvaluationProtocol(name="coding-oracle@3")
        verdict = self._claim(self._evaluator(
            candidate_digest=None, required_files=(), verification_subject_digest=None,
        ), protocol)
        self.assertEqual(verdict.claims[0]["event"], "EvaluationIncomplete")
        self.assertEqual(verdict.claims[0]["status"], "failed")
        self.assertEqual(verdict.reason, "empty_stub_solution")

    def test_pass_only_stub_is_rejected(self) -> None:
        self.a.write_text("def add(x, y):\n    pass\n", encoding="utf-8")
        self.b.write_text("def mul(x, y):\n    raise NotImplementedError\n", encoding="utf-8")
        live = _tree_digest({"pkg/a.py": self.a, "pkg/b.py": self.b})
        protocol = EvaluationProtocol(name="coding-oracle@3", parameters={
            "candidateDigest": live, "requiredFiles": list(self.required)})
        verdict = self._claim(self._evaluator(
            candidate_digest=live, verification_subject_digest=None), protocol)
        self.assertEqual(verdict.reason, "empty_stub_solution")
        self.assertEqual(verdict.claims[0]["status"], "failed")

    def test_vacuous_command_is_rejected_before_runner(self) -> None:
        called = False

        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            nonlocal called
            called = True
            return subprocess.CompletedProcess([], 0, b"", b"")

        verdict = self._claim(self._evaluator(
            command=("python3", "-c", "raise SystemExit(0)"), runner=runner))
        self.assertEqual(verdict.reason, "vacuous_discovery")
        self.assertFalse(called)

    def test_oracle_that_ignores_required_files_is_vacuous(self) -> None:
        self.oracle.write_text("assert True\n", encoding="utf-8")
        verdict = self._claim(self._evaluator(
            oracle_digests={"tests/test_oracle.py": _digest(self.oracle)}))
        self.assertEqual(verdict.reason, "vacuous_discovery")

    def test_omitted_required_file_is_rejected(self) -> None:
        self.b.unlink()
        live = _tree_digest({"pkg/a.py": self.a})
        protocol = EvaluationProtocol(name="coding-oracle@3", parameters={
            "candidateDigest": live, "requiredFiles": list(self.required)})
        verdict = self._claim(self._evaluator(candidate_digest=live), protocol)
        self.assertEqual(verdict.reason, "omitted_required_file")
        self.assertIn("pkg/b.py", verdict.claims[0]["details"])

    def test_unauthorized_addition_is_rejected(self) -> None:
        extra = self.workspace / "pkg" / "bonus.py"
        extra.write_text("BONUS = 1\n", encoding="utf-8")
        verdict = self._claim()
        self.assertEqual(verdict.reason, "unauthorized_addition")
        self.assertIn("pkg/bonus.py", verdict.claims[0]["details"])

    def test_candidate_substitution_is_rejected(self) -> None:
        foreign = "sha256:" + "b" * 64
        protocol = EvaluationProtocol(name="coding-oracle@3", parameters={
            "candidateDigest": foreign, "requiredFiles": list(self.required)})
        verdict = self._claim(protocol=protocol)
        self.assertEqual(verdict.reason, "candidate_substitution")
        self.assertEqual(verdict.claims[0]["candidateDigest"], self.live)

    def test_stale_verification_subject_is_rejected(self) -> None:
        stale = "sha256:" + "c" * 64
        protocol = EvaluationProtocol(name="coding-oracle@3", parameters={
            "candidateDigest": self.live,
            "requiredFiles": list(self.required),
            "verificationSubjectDigest": stale,
        })
        verdict = self._claim(protocol=protocol)
        self.assertEqual(verdict.reason, "stale_verification")

    def test_test_tampering_still_fails_before_completeness(self) -> None:
        sealed = _digest(self.oracle)
        self.oracle.write_text("assert False\n", encoding="utf-8")
        verdict = self._claim(self._evaluator(
            oracle_digests={"tests/test_oracle.py": sealed}))
        self.assertEqual(verdict.claims[0]["event"], "EvaluationTampered")
        self.assertFalse(verdict.claims[0]["probes"]["immutability"])

    def test_greenfield_single_module_positive_control(self) -> None:
        gf = Path(self._tmp.name) / "green"
        gf.mkdir()
        (gf / "retry.py").write_text(
            "def retry(fn, attempts=2):\n"
            "    if attempts < 1:\n"
            "        raise ValueError('attempts')\n"
            "    last = None\n"
            "    for _ in range(attempts):\n"
            "        try:\n"
            "            return fn()\n"
            "        except Exception as exc:\n"
            "            last = exc\n"
            "    raise last\n",
            encoding="utf-8",
        )
        (gf / "tests").mkdir()
        (gf / "tests" / "test_oracle.py").write_text(
            "from retry import retry\n"
            "assert retry(lambda: 7) == 7\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=gf, check=True)
        live = _tree_digest({"retry.py": gf / "retry.py"})
        protocol = EvaluationProtocol(name="coding-oracle@3", parameters={
            "candidateDigest": live, "requiredFiles": ["retry.py"]})
        evaluator = IsolatedEvaluator(
            workspace=gf,
            oracle_digests={"tests/test_oracle.py": _digest(gf / "tests" / "test_oracle.py")},
            command=("python3", "tests/test_oracle.py"),
            expected_uid=os.getuid(),
            image_digest="sha256:" + "a" * 64,
        )
        result = evaluator.evaluate(RunRef("gf", episode_id="ep-gf"), protocol)
        self.assertTrue(result.ok, result)
        verdict = result.value
        self.assertEqual(verdict.claims[0]["event"], "EvaluationCompleted")
        self.assertEqual(verdict.claims[0]["status"], "passed")
        self.assertEqual(verdict.claims[0]["candidateDigest"], live)
        self.assertNotIn("accepted", verdict.claims[0])


class TestT143ChildBinding(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self._tmp.name)
        (self.workspace / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
        (self.workspace / "tests").mkdir()
        self.oracle = self.workspace / "tests" / "test_oracle.py"
        self.oracle.write_text("from mod import VALUE\nassert VALUE == 1\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=self.workspace, check=True)
        subprocess.run(
            ["git", "add", "mod.py", "tests/test_oracle.py"],
            cwd=self.workspace, check=True,
        )
        self.live = _tree_digest({"mod.py": self.workspace / "mod.py"})
        self.protocol = EvaluationProtocol(name="coding-oracle@3", parameters={
            "candidateDigest": self.live, "requiredFiles": ["mod.py"],
            "verificationSubjectDigest": self.live,
        })

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_true_argv_is_vacuous_before_runner(self) -> None:
        called = False

        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            nonlocal called
            called = True
            return subprocess.CompletedProcess([], 0, b"", b"")

        evaluator = IsolatedEvaluator(
            workspace=self.workspace,
            oracle_digests={"tests/test_oracle.py": _digest(self.oracle)},
            command=("true",),
            expected_uid=os.getuid(),
            image_digest="sha256:" + "a" * 64,
            runner=runner,
        )
        result = evaluator.evaluate(RunRef("vacuous", episode_id="ep-v"), self.protocol)
        self.assertTrue(result.ok, result)
        self.assertEqual(result.value.reason, "vacuous_discovery")
        self.assertFalse(called)

    def test_oracle_child_binds_workspace_and_strips_host_pollution(self) -> None:
        captured: dict[str, object] = {}

        def runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            captured["env"] = kwargs.get("env")
            captured["cwd"] = kwargs.get("cwd")
            return subprocess.CompletedProcess(list(args[0]) if args else [], 0, b"", b"")

        previous = {
            key: os.environ.get(key)
            for key in ("PYTHONPATH", "PYTHONSTARTUP", "LD_PRELOAD")
        }
        os.environ["PYTHONPATH"] = "/evil/host/path"
        os.environ["PYTHONSTARTUP"] = "/evil/startup.py"
        os.environ["LD_PRELOAD"] = "/evil/lib.so"
        try:
            evaluator = IsolatedEvaluator(
                workspace=self.workspace,
                oracle_digests={"tests/test_oracle.py": _digest(self.oracle)},
                command=("python3", "tests/test_oracle.py"),
                expected_uid=os.getuid(),
                image_digest="sha256:" + "a" * 64,
                runner=runner,
            )
            result = evaluator.evaluate(RunRef("bind", episode_id="ep-bind"), self.protocol)
            self.assertTrue(result.ok, result)
            claim = result.value.claims[0]
            self.assertEqual(claim["event"], "EvaluationCompleted")
            self.assertNotIn("accepted", claim)
            env = captured["env"]
            self.assertIsInstance(env, dict)
            assert isinstance(env, dict)
            self.assertEqual(env.get("PYTHONPATH"), str(self.workspace.resolve()))
            self.assertNotIn("PYTHONSTARTUP", env)
            self.assertNotIn("LD_PRELOAD", env)
            self.assertEqual(captured["cwd"], self.workspace.resolve())
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == "__main__":
    unittest.main()
