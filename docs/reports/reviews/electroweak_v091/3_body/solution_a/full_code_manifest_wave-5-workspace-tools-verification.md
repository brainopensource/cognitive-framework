# Full Code Manifest — Wave 5: Workspace, Patching, Tools e Verificação Real

## 0. Resultado

Implementar uma superfície transacional de engenharia dentro de `packs/code-default`, usando os toolkits existentes e sem bypass do dispatch. A onda fecha edição atômica, rollback, comandos allowlisted, seleção de testes, receipts frescos e patch artifacts.

## 1. Paths reais reutilizados

- `packs/code-default/toolkits/fs_toolkit.py` — leitura/escrita confinada.
- `packs/code-default/toolkits/ast_patch.py` — patch estrutural/unified.
- `packs/code-default/toolkits/terminal_runner.py` — processos limitados.
- `packs/code-default/toolkits/composite.py` — resolução de verbs.
- `vanguard/packages/runtime/artifacts.py` — CAS/evidence.
- `vanguard/packages/agency/episode/admission_gate.py` — admissão.

## 2. Novo arquivo: `packs/code-default/coding_max/workspace_tx.py`

```python
from __future__ import annotations

import hashlib
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True, slots=True)
class WorkspaceState:
    digest: str
    changed_files: tuple[str, ...]
    deleted_files: tuple[str, ...]

class WorkspaceTransaction:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        if not (self.root / ".git").exists():
            raise ValueError("workspace must be a git repository")
        self._snapshot: Path | None = None
        self._baseline = self.state()

    def begin(self) -> None:
        if self._snapshot is not None:
            raise RuntimeError("transaction already active")
        self._snapshot = Path(tempfile.mkdtemp(prefix="aether-workspace-"))
        for path in self._tracked_files():
            target = self._snapshot / path.relative_to(self.root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)

    def commit(self) -> WorkspaceState:
        if self._snapshot is None:
            raise RuntimeError("no active transaction")
        state = self.state()
        shutil.rmtree(self._snapshot)
        self._snapshot = None
        self._baseline = state
        return state

    def rollback(self) -> WorkspaceState:
        if self._snapshot is None:
            raise RuntimeError("no active transaction")
        snapshot = self._snapshot
        current = {p.relative_to(self.root) for p in self._tracked_files()}
        original = {p.relative_to(snapshot) for p in snapshot.rglob("*") if p.is_file()}
        for relative in current - original:
            (self.root / relative).unlink()
        for relative in original:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(snapshot / relative, target)
        shutil.rmtree(snapshot, ignore_errors=True)
        self._snapshot = None
        return self.state()

    def state(self) -> WorkspaceState:
        current = {p.relative_to(self.root).as_posix(): self._hash(p) for p in self._tracked_files()}
        baseline = getattr(self, "_baseline", None)
        base_map = getattr(baseline, "_files", {}) if baseline else {}
        changed = tuple(sorted(path for path, digest in current.items() if base_map.get(path) != digest))
        deleted = tuple(sorted(set(base_map) - set(current)))
        aggregate = hashlib.sha256()
        for path, digest in sorted(current.items()):
            aggregate.update(path.encode())
            aggregate.update(digest.encode())
        state = WorkspaceState(aggregate.hexdigest(), changed, deleted)
        object.__setattr__(state, "_files", current)
        return state

    def changed_files(self) -> tuple[str, ...]:
        state = self.state()
        return tuple(sorted(set(state.changed_files) | set(state.deleted_files)))

    def digest(self) -> str:
        return self.state().digest

    def _tracked_files(self) -> Iterable[Path]:
        for path in self.root.rglob("*"):
            if path.is_file() and ".git" not in path.parts and "node_modules" not in path.parts:
                yield path

    @staticmethod
    def _hash(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()
```

## 3. Correção recomendada para produção

O exemplo acima documenta semântica, mas a implementação final deve trocar cópia ampla por `git worktree` ou snapshot por hardlink/reflink quando disponível. Nunca usar `git reset --hard`; rollback deve atuar somente no workspace efêmero criado para a execução.

## 4. Novo arquivo: `packs/code-default/coding_max/tool_results.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from vanguard.packages.runtime.artifacts import ArtifactWriter

@dataclass(frozen=True, slots=True)
class ToolResultRef:
    verb: str
    exit_code: int
    stdout_digest: str | None
    stderr_digest: str | None
    truncated: bool
    metadata: Mapping[str, Any]

class ToolResultCapturer:
    def __init__(self, writer: ArtifactWriter, *, run_id: str, episode_id: str, limit: int = 16000) -> None:
        self.writer = writer
        self.run_id = run_id
        self.episode_id = episode_id
        self.limit = limit

    def capture(self, *, verb: str, exit_code: int, stdout: str, stderr: str, metadata=None) -> ToolResultRef:
        out_ref = self.writer.capture(
            role="tool_stdout", payload=stdout, run_id=self.run_id,
            episode_id=self.episode_id, required=False,
        ) if stdout else None
        err_ref = self.writer.capture(
            role="tool_stderr", payload=stderr, run_id=self.run_id,
            episode_id=self.episode_id, required=False,
        ) if stderr else None
        return ToolResultRef(
            verb=verb, exit_code=exit_code,
            stdout_digest=out_ref.digest if out_ref else None,
            stderr_digest=err_ref.digest if err_ref else None,
            truncated=len(stdout) > self.limit or len(stderr) > self.limit,
            metadata=dict(metadata or {}),
        )
```

## 5. Novo arquivo: `packs/code-default/coding_max/test_selector.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .intelligence import RepositoryIntelligence

@dataclass(frozen=True, slots=True)
class TestPlan:
    targeted: tuple[tuple[str, ...], ...]
    affected: tuple[tuple[str, ...], ...]
    regression: tuple[tuple[str, ...], ...]

class TestSelector:
    def __init__(self, root: Path, intelligence: RepositoryIntelligence) -> None:
        self.root = root
        self.intelligence = intelligence

    def select(self, changed_files: Sequence[str], *, level: str) -> TestPlan:
        related = []
        for path in changed_files:
            related.extend(hit.path for hit in self.intelligence.tests_for(path))
        tests = tuple(dict.fromkeys(related))
        targeted = tuple(("python3", "-m", "pytest", test, "-q") for test in tests[:8])
        affected = (("python3", "-m", "pytest", *tests, "-q"),) if tests else ()
        regression = (("python3", "-m", "unittest", "discover", "-s", "test", "-t", "."),)
        if level == "targeted":
            return TestPlan(targeted, (), ())
        if level == "affected":
            return TestPlan(targeted, affected, ())
        if level == "regression":
            return TestPlan(targeted, affected, regression)
        raise ValueError(f"unknown verification level {level!r}")
```

## 6. Novo arquivo: `packs/code-default/coding_max/verification_pipeline.py`

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .verification import LayeredVerifier, VerificationResult

@dataclass(frozen=True, slots=True)
class VerificationBundle:
    workspace_digest: str
    results: tuple[VerificationResult, ...]
    passed: bool
    executed_test_count: int

class VerificationPipeline:
    def __init__(self, verifier: LayeredVerifier, workspace_digest: Callable[[], str]) -> None:
        self.verifier = verifier
        self.workspace_digest = workspace_digest

    def run(self, commands: Sequence[Sequence[str]]) -> VerificationBundle:
        before = self.workspace_digest()
        results = self.verifier.verify(commands)
        after = self.workspace_digest()
        if before != after:
            return VerificationBundle(after, results, False, sum(r.test_count for r in results))
        passed = bool(results) and all(result.passed for result in results)
        return VerificationBundle(
            workspace_digest=after, results=results, passed=passed,
            executed_test_count=sum(result.test_count for result in results),
        )
```

## 7. Diff em `terminal_runner.py`

```diff
@@ class TerminalToolkit:
-    def __init__(self, workspace: str | Path, timeout_seconds: float = 30.0) -> None:
+    def __init__(self, workspace: str | Path, timeout_seconds: float = 30.0,
+                 allowed_programs: Sequence[str] = ("git", "pytest", "python3", "ruff")) -> None:
         self._workspace = Path(workspace).resolve()
         self._timeout = timeout_seconds
+        self._allowed = frozenset(allowed_programs)
@@ def execute(self, request, ctx):
+        program = Path(command[0]).name
+        if program not in self._allowed:
+            return Err("program_denied", f"{program} is not allowlisted")
+        if request.args.get("cwd"):
+            cwd = (self._workspace / str(request.args["cwd"])).resolve()
+            if self._workspace not in cwd.parents and cwd != self._workspace:
+                return Err("cwd_escape", "cwd escapes workspace")
```

## 8. Diff em `fs_toolkit.py`

```diff
@@ class FsToolkit:
+    def _resolve(self, raw: str) -> Path:
+        target = (self._workspace / raw).resolve()
+        if target != self._workspace and self._workspace not in target.parents:
+            raise ValueError("path escapes workspace")
+        return target
@@ def execute(self, request, ctx):
-        path = self._workspace / str(request.args["path"])
+        try:
+            path = self._resolve(str(request.args["path"]))
+        except ValueError as exc:
+            return Err("path_escape", str(exc))
```

## 9. Diff em `ast_patch.py`

```diff
@@ class AstPatchToolkit:
+        expected = str(request.args.get("before_digest") or "")
+        current = hashlib.sha256(before.encode("utf-8")).hexdigest()
+        if expected and expected != current:
+            return Err("stale_patch", "before_digest does not match current file")
+        if after == before:
+            return Err("no_op_patch", "patch produced no change")
+        temp = path.with_suffix(path.suffix + ".aether-tmp")
+        temp.write_text(after, encoding="utf-8")
+        os.replace(temp, path)
```

## 10. Testes: `test/packs/code_default/test_workspace_tools.py`

```python
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from coding_max.verification import LayeredVerifier
from coding_max.verification_pipeline import VerificationPipeline

class VerificationPipelineTests(unittest.TestCase):
    def test_zero_tests_is_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            verifier = LayeredVerifier(Path(tmp))
            pipeline = VerificationPipeline(verifier, lambda: "same")
            bundle = pipeline.run((("python3", "-c", "print('ok')"),))
            self.assertFalse(bundle.passed)

    def test_workspace_mutation_during_tests_is_stale(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker = root / "marker"
            digest = lambda: marker.read_text() if marker.exists() else "before"
            verifier = LayeredVerifier(root)
            pipeline = VerificationPipeline(verifier, digest)
            command = ("python3", "-c", "open('marker','w').write('after'); print('1 passed')")
            bundle = pipeline.run((command,))
            self.assertFalse(bundle.passed)

    def test_observed_tests_pass_on_unchanged_subject(self):
        with tempfile.TemporaryDirectory() as tmp:
            verifier = LayeredVerifier(Path(tmp))
            pipeline = VerificationPipeline(verifier, lambda: "stable")
            bundle = pipeline.run((("python3", "-c", "print('2 passed')"),))
            self.assertTrue(bundle.passed)
            self.assertEqual(bundle.executed_test_count, 2)
```

## 11. Security invariants

| ID | Invariant | Falsifier |
|---|---|---|
| WS-001 | No path traversal | adversarial focused test |
| WS-002 | No cwd escape | adversarial focused test |
| WS-003 | No unallowlisted executable | adversarial focused test |
| WS-004 | No stale patch | adversarial focused test |
| WS-005 | No no-op patch | adversarial focused test |
| WS-006 | Atomic file replacement | adversarial focused test |
| WS-007 | Rollback only in ephemeral workspace | adversarial focused test |
| WS-008 | Stdout/stderr artifact-backed | adversarial focused test |
| WS-009 | Output truncation explicit | adversarial focused test |
| WS-010 | Tests cannot mutate subject silently | adversarial focused test |
| WS-011 | Zero tests rejected | adversarial focused test |
| WS-012 | Timeout typed | adversarial focused test |
| WS-013 | Exit code preserved | adversarial focused test |
| WS-014 | Changed files derived physically | adversarial focused test |
| WS-015 | Patch digest bound to before/after | adversarial focused test |
| WS-016 | Symlink escape rejected | adversarial focused test |
| WS-017 | Secrets redacted by ArtifactWriter | adversarial focused test |
| WS-018 | No shell=True | adversarial focused test |
| WS-019 | No implicit network | adversarial focused test |
| WS-020 | No destructive git reset | adversarial focused test |

## 12. Tool contracts

| Verb | Inputs | Receipt | Recoverable failures |
|---|---|---|---|
| fs.read | path/range | digest, bytes | missing/range |
| fs.search | query/globs | matches artifact | no matches |
| patch.apply | path/diff/before_digest | before/after/diff digests | stale/conflict |
| proc.exec | argv/cwd/timeout | exit/stdout/stderr digests | timeout/nonzero |
| test.run | selection/level | counts/duration/workspace digest | fail/zero/stale |
| git.diff | base/path | diff artifact | dirty baseline |

## 13. Test corpus obrigatório

- traversal `../../etc/passwd`.
- absolute path fora da raiz.
- symlink interno apontando para fora.
- patch com digest antigo.
- patch que não altera bytes.
- patch parcialmente aplicável.
- processo não allowlisted.
- processo que excede timeout.
- output acima do limite.
- testes com exit 0 e zero count.
- testes com exit 1 e count positivo.
- testes que alteram workspace.
- rollback após patch inválido.
- commit após patch válido.
- arquivo binário rejeitado por editor textual.
- concorrência sobre o mesmo arquivo recusada.

## 14. Ordem de integração

1. Implementar `_resolve` comum e testes de escape.
2. Implementar atomic patch com `before_digest`.
3. Adicionar captura artifact-backed de resultados.
4. Implementar TestSelector.
5. Implementar VerificationPipeline.
6. Integrar transaction begin/commit/rollback no coordinator.
7. Rodar smoke em repositório temporário.
8. Só depois habilitar `coding-max` em runs reais.

## 15. Review checklist detalhado

- [ ] WS-R001 — `WorkspaceTransaction.begin` validates root.
- [ ] WS-R002 — `WorkspaceTransaction.begin` rejects traversal.
- [ ] WS-R003 — `WorkspaceTransaction.begin` handles symlink.
- [ ] WS-R004 — `WorkspaceTransaction.begin` preserves digest.
- [ ] WS-R005 — `WorkspaceTransaction.begin` returns typed error.
- [ ] WS-R006 — `WorkspaceTransaction.begin` records artifact.
- [ ] WS-R007 — `WorkspaceTransaction.begin` propagates budget.
- [ ] WS-R008 — `WorkspaceTransaction.begin` has timeout.
- [ ] WS-R009 — `WorkspaceTransaction.begin` is idempotent.
- [ ] WS-R010 — `WorkspaceTransaction.begin` supports retry.
- [ ] WS-R011 — `WorkspaceTransaction.begin` does not use shell.
- [ ] WS-R012 — `WorkspaceTransaction.begin` does not leak secret.
- [ ] WS-R013 — `WorkspaceTransaction.begin` bounds output.
- [ ] WS-R014 — `WorkspaceTransaction.begin` tests success.
- [ ] WS-R015 — `WorkspaceTransaction.begin` tests failure.
- [ ] WS-R016 — `WorkspaceTransaction.begin` tests stale input.
- [ ] WS-R017 — `WorkspaceTransaction.begin` tests interruption.
- [ ] WS-R018 — `WorkspaceTransaction.begin` tests rollback.
- [ ] WS-R019 — `WorkspaceTransaction.begin` documents failure.
- [ ] WS-R020 — `WorkspaceTransaction.begin` keeps authority in kernel.
- [ ] WS-R021 — `WorkspaceTransaction.begin` works offline.
- [ ] WS-R022 — `WorkspaceTransaction.begin` uses atomic replace.
- [ ] WS-R023 — `WorkspaceTransaction.begin` reports changed files.
- [ ] WS-R024 — `WorkspaceTransaction.begin` binds workspace identity.
- [ ] WS-R025 — `WorkspaceTransaction.begin` avoids full repo copy when possible.
- [ ] WS-R026 — `WorkspaceTransaction.commit` validates root.
- [ ] WS-R027 — `WorkspaceTransaction.commit` rejects traversal.
- [ ] WS-R028 — `WorkspaceTransaction.commit` handles symlink.
- [ ] WS-R029 — `WorkspaceTransaction.commit` preserves digest.
- [ ] WS-R030 — `WorkspaceTransaction.commit` returns typed error.
- [ ] WS-R031 — `WorkspaceTransaction.commit` records artifact.
- [ ] WS-R032 — `WorkspaceTransaction.commit` propagates budget.
- [ ] WS-R033 — `WorkspaceTransaction.commit` has timeout.
- [ ] WS-R034 — `WorkspaceTransaction.commit` is idempotent.
- [ ] WS-R035 — `WorkspaceTransaction.commit` supports retry.
- [ ] WS-R036 — `WorkspaceTransaction.commit` does not use shell.
- [ ] WS-R037 — `WorkspaceTransaction.commit` does not leak secret.
- [ ] WS-R038 — `WorkspaceTransaction.commit` bounds output.
- [ ] WS-R039 — `WorkspaceTransaction.commit` tests success.
- [ ] WS-R040 — `WorkspaceTransaction.commit` tests failure.
- [ ] WS-R041 — `WorkspaceTransaction.commit` tests stale input.
- [ ] WS-R042 — `WorkspaceTransaction.commit` tests interruption.
- [ ] WS-R043 — `WorkspaceTransaction.commit` tests rollback.
- [ ] WS-R044 — `WorkspaceTransaction.commit` documents failure.
- [ ] WS-R045 — `WorkspaceTransaction.commit` keeps authority in kernel.
- [ ] WS-R046 — `WorkspaceTransaction.commit` works offline.
- [ ] WS-R047 — `WorkspaceTransaction.commit` uses atomic replace.
- [ ] WS-R048 — `WorkspaceTransaction.commit` reports changed files.
- [ ] WS-R049 — `WorkspaceTransaction.commit` binds workspace identity.
- [ ] WS-R050 — `WorkspaceTransaction.commit` avoids full repo copy when possible.
- [ ] WS-R051 — `WorkspaceTransaction.rollback` validates root.
- [ ] WS-R052 — `WorkspaceTransaction.rollback` rejects traversal.
- [ ] WS-R053 — `WorkspaceTransaction.rollback` handles symlink.
- [ ] WS-R054 — `WorkspaceTransaction.rollback` preserves digest.
- [ ] WS-R055 — `WorkspaceTransaction.rollback` returns typed error.
- [ ] WS-R056 — `WorkspaceTransaction.rollback` records artifact.
- [ ] WS-R057 — `WorkspaceTransaction.rollback` propagates budget.
- [ ] WS-R058 — `WorkspaceTransaction.rollback` has timeout.
- [ ] WS-R059 — `WorkspaceTransaction.rollback` is idempotent.
- [ ] WS-R060 — `WorkspaceTransaction.rollback` supports retry.
- [ ] WS-R061 — `WorkspaceTransaction.rollback` does not use shell.
- [ ] WS-R062 — `WorkspaceTransaction.rollback` does not leak secret.
- [ ] WS-R063 — `WorkspaceTransaction.rollback` bounds output.
- [ ] WS-R064 — `WorkspaceTransaction.rollback` tests success.
- [ ] WS-R065 — `WorkspaceTransaction.rollback` tests failure.
- [ ] WS-R066 — `WorkspaceTransaction.rollback` tests stale input.
- [ ] WS-R067 — `WorkspaceTransaction.rollback` tests interruption.
- [ ] WS-R068 — `WorkspaceTransaction.rollback` tests rollback.
- [ ] WS-R069 — `WorkspaceTransaction.rollback` documents failure.
- [ ] WS-R070 — `WorkspaceTransaction.rollback` keeps authority in kernel.
- [ ] WS-R071 — `WorkspaceTransaction.rollback` works offline.
- [ ] WS-R072 — `WorkspaceTransaction.rollback` uses atomic replace.
- [ ] WS-R073 — `WorkspaceTransaction.rollback` reports changed files.
- [ ] WS-R074 — `WorkspaceTransaction.rollback` binds workspace identity.
- [ ] WS-R075 — `WorkspaceTransaction.rollback` avoids full repo copy when possible.
- [ ] WS-R076 — `WorkspaceTransaction.state` validates root.
- [ ] WS-R077 — `WorkspaceTransaction.state` rejects traversal.
- [ ] WS-R078 — `WorkspaceTransaction.state` handles symlink.
- [ ] WS-R079 — `WorkspaceTransaction.state` preserves digest.
- [ ] WS-R080 — `WorkspaceTransaction.state` returns typed error.
- [ ] WS-R081 — `WorkspaceTransaction.state` records artifact.
- [ ] WS-R082 — `WorkspaceTransaction.state` propagates budget.
- [ ] WS-R083 — `WorkspaceTransaction.state` has timeout.
- [ ] WS-R084 — `WorkspaceTransaction.state` is idempotent.
- [ ] WS-R085 — `WorkspaceTransaction.state` supports retry.
- [ ] WS-R086 — `WorkspaceTransaction.state` does not use shell.
- [ ] WS-R087 — `WorkspaceTransaction.state` does not leak secret.
- [ ] WS-R088 — `WorkspaceTransaction.state` bounds output.
- [ ] WS-R089 — `WorkspaceTransaction.state` tests success.
- [ ] WS-R090 — `WorkspaceTransaction.state` tests failure.
- [ ] WS-R091 — `WorkspaceTransaction.state` tests stale input.
- [ ] WS-R092 — `WorkspaceTransaction.state` tests interruption.
- [ ] WS-R093 — `WorkspaceTransaction.state` tests rollback.
- [ ] WS-R094 — `WorkspaceTransaction.state` documents failure.
- [ ] WS-R095 — `WorkspaceTransaction.state` keeps authority in kernel.
- [ ] WS-R096 — `WorkspaceTransaction.state` works offline.
- [ ] WS-R097 — `WorkspaceTransaction.state` uses atomic replace.
- [ ] WS-R098 — `WorkspaceTransaction.state` reports changed files.
- [ ] WS-R099 — `WorkspaceTransaction.state` binds workspace identity.
- [ ] WS-R100 — `WorkspaceTransaction.state` avoids full repo copy when possible.
- [ ] WS-R101 — `ToolResultCapturer.capture` validates root.
- [ ] WS-R102 — `ToolResultCapturer.capture` rejects traversal.
- [ ] WS-R103 — `ToolResultCapturer.capture` handles symlink.
- [ ] WS-R104 — `ToolResultCapturer.capture` preserves digest.
- [ ] WS-R105 — `ToolResultCapturer.capture` returns typed error.
- [ ] WS-R106 — `ToolResultCapturer.capture` records artifact.
- [ ] WS-R107 — `ToolResultCapturer.capture` propagates budget.
- [ ] WS-R108 — `ToolResultCapturer.capture` has timeout.
- [ ] WS-R109 — `ToolResultCapturer.capture` is idempotent.
- [ ] WS-R110 — `ToolResultCapturer.capture` supports retry.
- [ ] WS-R111 — `ToolResultCapturer.capture` does not use shell.
- [ ] WS-R112 — `ToolResultCapturer.capture` does not leak secret.
- [ ] WS-R113 — `ToolResultCapturer.capture` bounds output.
- [ ] WS-R114 — `ToolResultCapturer.capture` tests success.
- [ ] WS-R115 — `ToolResultCapturer.capture` tests failure.
- [ ] WS-R116 — `ToolResultCapturer.capture` tests stale input.
- [ ] WS-R117 — `ToolResultCapturer.capture` tests interruption.
- [ ] WS-R118 — `ToolResultCapturer.capture` tests rollback.
- [ ] WS-R119 — `ToolResultCapturer.capture` documents failure.
- [ ] WS-R120 — `ToolResultCapturer.capture` keeps authority in kernel.
- [ ] WS-R121 — `ToolResultCapturer.capture` works offline.
- [ ] WS-R122 — `ToolResultCapturer.capture` uses atomic replace.
- [ ] WS-R123 — `ToolResultCapturer.capture` reports changed files.
- [ ] WS-R124 — `ToolResultCapturer.capture` binds workspace identity.
- [ ] WS-R125 — `ToolResultCapturer.capture` avoids full repo copy when possible.
- [ ] WS-R126 — `TestSelector.select` validates root.
- [ ] WS-R127 — `TestSelector.select` rejects traversal.
- [ ] WS-R128 — `TestSelector.select` handles symlink.
- [ ] WS-R129 — `TestSelector.select` preserves digest.
- [ ] WS-R130 — `TestSelector.select` returns typed error.
- [ ] WS-R131 — `TestSelector.select` records artifact.
- [ ] WS-R132 — `TestSelector.select` propagates budget.
- [ ] WS-R133 — `TestSelector.select` has timeout.
- [ ] WS-R134 — `TestSelector.select` is idempotent.
- [ ] WS-R135 — `TestSelector.select` supports retry.
- [ ] WS-R136 — `TestSelector.select` does not use shell.
- [ ] WS-R137 — `TestSelector.select` does not leak secret.
- [ ] WS-R138 — `TestSelector.select` bounds output.
- [ ] WS-R139 — `TestSelector.select` tests success.
- [ ] WS-R140 — `TestSelector.select` tests failure.
- [ ] WS-R141 — `TestSelector.select` tests stale input.
- [ ] WS-R142 — `TestSelector.select` tests interruption.
- [ ] WS-R143 — `TestSelector.select` tests rollback.
- [ ] WS-R144 — `TestSelector.select` documents failure.
- [ ] WS-R145 — `TestSelector.select` keeps authority in kernel.
- [ ] WS-R146 — `TestSelector.select` works offline.
- [ ] WS-R147 — `TestSelector.select` uses atomic replace.
- [ ] WS-R148 — `TestSelector.select` reports changed files.
- [ ] WS-R149 — `TestSelector.select` binds workspace identity.
- [ ] WS-R150 — `TestSelector.select` avoids full repo copy when possible.
- [ ] WS-R151 — `VerificationPipeline.run` validates root.
- [ ] WS-R152 — `VerificationPipeline.run` rejects traversal.
- [ ] WS-R153 — `VerificationPipeline.run` handles symlink.
- [ ] WS-R154 — `VerificationPipeline.run` preserves digest.
- [ ] WS-R155 — `VerificationPipeline.run` returns typed error.
- [ ] WS-R156 — `VerificationPipeline.run` records artifact.
- [ ] WS-R157 — `VerificationPipeline.run` propagates budget.
- [ ] WS-R158 — `VerificationPipeline.run` has timeout.
- [ ] WS-R159 — `VerificationPipeline.run` is idempotent.
- [ ] WS-R160 — `VerificationPipeline.run` supports retry.
- [ ] WS-R161 — `VerificationPipeline.run` does not use shell.
- [ ] WS-R162 — `VerificationPipeline.run` does not leak secret.
- [ ] WS-R163 — `VerificationPipeline.run` bounds output.
- [ ] WS-R164 — `VerificationPipeline.run` tests success.
- [ ] WS-R165 — `VerificationPipeline.run` tests failure.
- [ ] WS-R166 — `VerificationPipeline.run` tests stale input.
- [ ] WS-R167 — `VerificationPipeline.run` tests interruption.
- [ ] WS-R168 — `VerificationPipeline.run` tests rollback.
- [ ] WS-R169 — `VerificationPipeline.run` documents failure.
- [ ] WS-R170 — `VerificationPipeline.run` keeps authority in kernel.
- [ ] WS-R171 — `VerificationPipeline.run` works offline.
- [ ] WS-R172 — `VerificationPipeline.run` uses atomic replace.
- [ ] WS-R173 — `VerificationPipeline.run` reports changed files.
- [ ] WS-R174 — `VerificationPipeline.run` binds workspace identity.
- [ ] WS-R175 — `VerificationPipeline.run` avoids full repo copy when possible.
- [ ] WS-R176 — `TerminalToolkit.execute` validates root.
- [ ] WS-R177 — `TerminalToolkit.execute` rejects traversal.
- [ ] WS-R178 — `TerminalToolkit.execute` handles symlink.
- [ ] WS-R179 — `TerminalToolkit.execute` preserves digest.
- [ ] WS-R180 — `TerminalToolkit.execute` returns typed error.
- [ ] WS-R181 — `TerminalToolkit.execute` records artifact.
- [ ] WS-R182 — `TerminalToolkit.execute` propagates budget.
- [ ] WS-R183 — `TerminalToolkit.execute` has timeout.
- [ ] WS-R184 — `TerminalToolkit.execute` is idempotent.
- [ ] WS-R185 — `TerminalToolkit.execute` supports retry.
- [ ] WS-R186 — `TerminalToolkit.execute` does not use shell.
- [ ] WS-R187 — `TerminalToolkit.execute` does not leak secret.
- [ ] WS-R188 — `TerminalToolkit.execute` bounds output.
- [ ] WS-R189 — `TerminalToolkit.execute` tests success.
- [ ] WS-R190 — `TerminalToolkit.execute` tests failure.
- [ ] WS-R191 — `TerminalToolkit.execute` tests stale input.
- [ ] WS-R192 — `TerminalToolkit.execute` tests interruption.
- [ ] WS-R193 — `TerminalToolkit.execute` tests rollback.
- [ ] WS-R194 — `TerminalToolkit.execute` documents failure.
- [ ] WS-R195 — `TerminalToolkit.execute` keeps authority in kernel.
- [ ] WS-R196 — `TerminalToolkit.execute` works offline.
- [ ] WS-R197 — `TerminalToolkit.execute` uses atomic replace.
- [ ] WS-R198 — `TerminalToolkit.execute` reports changed files.
- [ ] WS-R199 — `TerminalToolkit.execute` binds workspace identity.
- [ ] WS-R200 — `TerminalToolkit.execute` avoids full repo copy when possible.
- [ ] WS-R201 — `FsToolkit.execute` validates root.
- [ ] WS-R202 — `FsToolkit.execute` rejects traversal.
- [ ] WS-R203 — `FsToolkit.execute` handles symlink.
- [ ] WS-R204 — `FsToolkit.execute` preserves digest.
- [ ] WS-R205 — `FsToolkit.execute` returns typed error.
- [ ] WS-R206 — `FsToolkit.execute` records artifact.
- [ ] WS-R207 — `FsToolkit.execute` propagates budget.
- [ ] WS-R208 — `FsToolkit.execute` has timeout.
- [ ] WS-R209 — `FsToolkit.execute` is idempotent.
- [ ] WS-R210 — `FsToolkit.execute` supports retry.
- [ ] WS-R211 — `FsToolkit.execute` does not use shell.
- [ ] WS-R212 — `FsToolkit.execute` does not leak secret.
- [ ] WS-R213 — `FsToolkit.execute` bounds output.
- [ ] WS-R214 — `FsToolkit.execute` tests success.
- [ ] WS-R215 — `FsToolkit.execute` tests failure.
- [ ] WS-R216 — `FsToolkit.execute` tests stale input.
- [ ] WS-R217 — `FsToolkit.execute` tests interruption.
- [ ] WS-R218 — `FsToolkit.execute` tests rollback.
- [ ] WS-R219 — `FsToolkit.execute` documents failure.
- [ ] WS-R220 — `FsToolkit.execute` keeps authority in kernel.
- [ ] WS-R221 — `FsToolkit.execute` works offline.
- [ ] WS-R222 — `FsToolkit.execute` uses atomic replace.
- [ ] WS-R223 — `FsToolkit.execute` reports changed files.
- [ ] WS-R224 — `FsToolkit.execute` binds workspace identity.
- [ ] WS-R225 — `FsToolkit.execute` avoids full repo copy when possible.
- [ ] WS-R226 — `AstPatchToolkit.execute` validates root.
- [ ] WS-R227 — `AstPatchToolkit.execute` rejects traversal.
- [ ] WS-R228 — `AstPatchToolkit.execute` handles symlink.
- [ ] WS-R229 — `AstPatchToolkit.execute` preserves digest.
- [ ] WS-R230 — `AstPatchToolkit.execute` returns typed error.
- [ ] WS-R231 — `AstPatchToolkit.execute` records artifact.
- [ ] WS-R232 — `AstPatchToolkit.execute` propagates budget.
- [ ] WS-R233 — `AstPatchToolkit.execute` has timeout.
- [ ] WS-R234 — `AstPatchToolkit.execute` is idempotent.
- [ ] WS-R235 — `AstPatchToolkit.execute` supports retry.
- [ ] WS-R236 — `AstPatchToolkit.execute` does not use shell.
- [ ] WS-R237 — `AstPatchToolkit.execute` does not leak secret.
- [ ] WS-R238 — `AstPatchToolkit.execute` bounds output.
- [ ] WS-R239 — `AstPatchToolkit.execute` tests success.
- [ ] WS-R240 — `AstPatchToolkit.execute` tests failure.
- [ ] WS-R241 — `AstPatchToolkit.execute` tests stale input.
- [ ] WS-R242 — `AstPatchToolkit.execute` tests interruption.
- [ ] WS-R243 — `AstPatchToolkit.execute` tests rollback.
- [ ] WS-R244 — `AstPatchToolkit.execute` documents failure.
- [ ] WS-R245 — `AstPatchToolkit.execute` keeps authority in kernel.
- [ ] WS-R246 — `AstPatchToolkit.execute` works offline.
- [ ] WS-R247 — `AstPatchToolkit.execute` uses atomic replace.
- [ ] WS-R248 — `AstPatchToolkit.execute` reports changed files.
- [ ] WS-R249 — `AstPatchToolkit.execute` binds workspace identity.
- [ ] WS-R250 — `AstPatchToolkit.execute` avoids full repo copy when possible.

## 16. Acceptance gates

- [ ] Patch real altera bytes dentro do workspace.
- [ ] Receipt contém before/after/diff digests.
- [ ] Teste real executa e count é observado.
- [ ] Digest do workspace é igual antes/depois da verificação.
- [ ] Falha restaura snapshot sem tocar checkout do usuário.
- [ ] Nenhum command usa `shell=True`.
- [ ] Nenhum path escapa via `..`, absoluto ou symlink.
- [ ] Artifacts grandes ficam no CAS.
- [ ] Coordinator recebe somente referências compactas.
- [ ] AdmissionGate consome receipt fresco.

## 17. Definition of Done

A onda termina com um smoke `task → edit atômico → teste real → receipt fresco → commit`, mais falsificadores de traversal, stale patch, zero-test, timeout e rollback. Qualquer resultado sem patch físico e execução observada permanece não concluído.

- [ ] WS-X657 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X658 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X659 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X660 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X661 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X662 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X663 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X664 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X665 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X666 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X667 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X668 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X669 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X670 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X671 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X672 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X673 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X674 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X675 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X676 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X677 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X678 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X679 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X680 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X681 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X682 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X683 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X684 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X685 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X686 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X687 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X688 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X689 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X690 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X691 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X692 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X693 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X694 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X695 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X696 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X697 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X698 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X699 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X700 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X701 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X702 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X703 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X704 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X705 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X706 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X707 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X708 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X709 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X710 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X711 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X712 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X713 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X714 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X715 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X716 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X717 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X718 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X719 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X720 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X721 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X722 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X723 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X724 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X725 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X726 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X727 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X728 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X729 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X730 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X731 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X732 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X733 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X734 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X735 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X736 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X737 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X738 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X739 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X740 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X741 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X742 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X743 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X744 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X745 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X746 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X747 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X748 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X749 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X750 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X751 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X752 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X753 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X754 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X755 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X756 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X757 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X758 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X759 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X760 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X761 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X762 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X763 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X764 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X765 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X766 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X767 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X768 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X769 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X770 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X771 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X772 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X773 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X774 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X775 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X776 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X777 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X778 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X779 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X780 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X781 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X782 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X783 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X784 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X785 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X786 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X787 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X788 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X789 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X790 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X791 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X792 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X793 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X794 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X795 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X796 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X797 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X798 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X799 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X800 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X801 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X802 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X803 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X804 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X805 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X806 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X807 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X808 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X809 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X810 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X811 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X812 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X813 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X814 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X815 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X816 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X817 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X818 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X819 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X820 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X821 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X822 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X823 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X824 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X825 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X826 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X827 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X828 — Validar obrigação transacional remanescente antes de integrar.
- [ ] WS-X829 — Validar obrigação transacional remanescente antes de integrar.
