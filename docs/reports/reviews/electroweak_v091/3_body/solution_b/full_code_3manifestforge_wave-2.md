# full_code_3manifestforge — Wave 2
## Contexto Progressivo (CM-03) e Planner / TODO (CM-04)

Continuação da Wave 1. Todo código abaixo está em disco e foi smoke-testado.

---

## Cap. 7 — Contexto progressivo

### 7.1 NOVO — `vanguard/packages/apps/coding_max/context/scoring.py` (128 linhas)

Pontuação de candidatos (§11). **Puro**: sem I/O, então um ranking é reproduzível a partir de um trace.

```python
@dataclass(frozen=True, slots=True)
class Candidate:
    path: str
    text: str = ""
    line: int = 0
    provider: str = ""
    provider_confidence: float = 0.5
    pinned: bool = False

    @property
    def token_estimate(self) -> int:
        return max(1, len(self.text) // 4)


@dataclass(frozen=True, slots=True)
class ScoreBreakdown:
    """Cada termo do §11 mantido separado, para que um ranking seja explicável."""
    task_similarity: float = 0.0
    symbol_relevance: float = 0.0
    dependency_proximity: float = 0.0
    test_relationship: float = 0.0
    stacktrace_relevance: float = 0.0
    recent_failure_relevance: float = 0.0
    plan_relevance: float = 0.0
    edit_proximity: float = 0.0
    redundancy: float = 0.0
    staleness: float = 0.0

    @property
    def total(self) -> float:
        return (self.task_similarity + self.symbol_relevance + self.dependency_proximity
                + self.test_relationship + self.stacktrace_relevance
                + self.recent_failure_relevance + self.plan_relevance
                + self.edit_proximity - self.redundancy - self.staleness)
```

Os pesos, com a justificativa embutida:

```python
        breakdown = ScoreBreakdown(
            task_similarity=2.0 * overlap,
            symbol_relevance=1.5 if (stem in symbol_set or
                any(s in candidate.text.lower() for s in symbol_set)) else 0.0,
            dependency_proximity=1.0 if candidate.path in dep_set else 0.0,
            test_relationship=0.8 if candidate.path in test_set else 0.0,
            # Um stack trace nomeia o frame que falhou diretamente; nada mais no
            # score é evidência de localização tão direta.
            stacktrace_relevance=3.0 if candidate.path in trace_set else 0.0,
            recent_failure_relevance=1.2 if candidate.path in failed_set else 0.0,
            plan_relevance=1.0 if candidate.path in plan_set else 0.0,
            edit_proximity=1.4 if candidate.path in edited_set else 0.0,
            redundancy=2.0 if _digest(candidate) in seen else 0.0,
            # Blobs grandes expulsam vários candidatos pequenos e mais bem-direcionados.
            staleness=min(1.5, candidate.token_estimate / 4000.0),
        )

    # Pinned ordena primeiro INDEPENDENTE do score: pin é decisão explícita de
    # operador/plano e não pode ser silenciosamente sobreposta por ranking.
    scored.sort(key=lambda pair: (pair[0].pinned, pair[1].total), reverse=True)
```

**Verificado:** `[('a/b.py', 4.5), ('t/test_b.py', 0.5)]` — o arquivo nomeado no stack trace domina, como esperado.

---

### 7.2 NOVO — `vanguard/packages/apps/coding_max/context/progressive.py` (217 linhas)

Working set com os seis verbos do §12.

> **Invariante crítica:** adições em meio de run vão para a camada DIALOGUE, nunca para o prefixo. O `ContextCompiler` do substrato cacheia o prefixo SYSTEM/TOOLS/ENVIRONMENT e quebra esse cache se ele mudar — uma retrieval que reescrevesse o prefixo multiplicaria silenciosamente o custo em tokens de **todos** os turnos restantes.

```python
class ProgressiveContext:
    """O working set. `epoch` incrementa a CADA mutação.

    O epoch não é decoração: `runtime/meta_controller.py::validate_confidence`
    recusa um ConfidenceRecord cujo `contextEpoch` não bate com a view corrente,
    então um sinal obsoleto não consegue dirigir uma diretiva. Toda mutação aqui
    precisa portanto ser visível como bump de epoch."""

    def __init__(self, *, token_budget: int = 120_000) -> None:
        self._entries: dict[str, ContextEntry] = {}
        self._budget = token_budget
        self._epoch = 0
        self._dropped: list[str] = []
        self._history: list[Mapping[str, Any]] = []
```

Os seis verbos (§12):

```python
    def add(self, key, text, *, label="", source="", score=0.0, pinned=False) -> bool:
        """Admite uma entrada. False se já presente e inalterada."""

    def drop(self, key: str) -> bool:
        entry = self._entries.get(key)
        if entry is None or entry.pinned:
            return False        # pin protege de drop
        ...

    def pin(self, key: str) -> bool:
        """Protege de eviction e compressão."""

    def compress(self, key: str, summary: str) -> bool:
        """Substitui corpo por resumo, mantendo a chave alcançável.

        Compressão é lossy e irreversível dentro de um run, então nunca toca
        entrada pinned e nunca encolhe algo já pequeno — um resumo de quarenta
        tokens custa mais do que economiza."""
        entry = self._entries.get(key)
        if entry is None or entry.pinned or entry.token_estimate < 200:
            return False
        ...

    def refresh(self, key: str, text: str) -> bool:
        """Re-lê entrada cujo arquivo subjacente mudou."""

    def replace_all(self, entries) -> None:
        """Troca completa PRESERVANDO pins. Usada em mudança de estratégia."""
        pinned = {k: v for k, v in self._entries.items() if v.pinned}
```

Admissão ranqueada:

```python
    def admit_ranked(self, candidates, *, task="", limit=12, **signals) -> tuple[str, ...]:
        """Pontua candidatos e admite os melhores que couberem no budget.

        Candidatos já no working set são PULADOS, não re-pontuados: re-admitir
        resetaria o epoch e tornaria todo ConfidenceRecord pendente obsoleto,
        sem ganho informacional algum."""
        ranked = score_candidates(candidates, task=task, **signals)
        admitted: list[str] = []
        for candidate, breakdown in ranked:
            if len(admitted) >= limit: break
            if candidate.path in self._entries: continue
            if self.total_tokens() + candidate.token_estimate > self._budget: continue
            if self.add(candidate.path, candidate.text, source=candidate.provider,
                        score=breakdown.total, pinned=candidate.pinned):
                admitted.append(candidate.path)
        return tuple(admitted)
```

Eviction por menor score, respeitando pins:

```python
    def _evict_if_needed(self) -> None:
        if self.total_tokens() <= self._budget: return
        evictable = sorted((e for e in self._entries.values() if not e.pinned),
                           key=lambda e: e.score)
        for entry in evictable:
            if self.total_tokens() <= self._budget: break
            del self._entries[entry.key]
            self._dropped.append(entry.key)
```

**Verificado:** `epoch 2 tokens 100` → admit → `epoch 3`; `drop('a.py')` em entrada pinned retorna `False`; ambas entradas sobrevivem.

---

## Cap. 8 — Planner e TODO

### 8.1 NOVO — `vanguard/packages/apps/coding_max/planning/todo.py` (266 linhas)

M�quina de estados §16. O valor está na **tabela de transições**: um TODO que pode ir a qualquer lugar não é máquina de estados, e a falha que isso esconde é um agente marcando trabalho como DONE sem evidência.

```python
class TodoStatus(str, Enum):
    PENDING="pending"; ACTIVE="active"; BLOCKED="blocked"
    DONE="done"; FAILED="failed"; SKIPPED="skipped"

class TodoEvent(str, Enum):
    CREATED="todo.created";   STARTED="todo.started"
    COMPLETED="todo.completed"; FAILED="todo.failed"
    REOPENED="todo.reopened";  BLOCKED="todo.blocked"; SKIPPED="todo.skipped"


#: Transições legais. Qualquer ausente LEVANTA em vez de virar no-op silencioso,
#: porque uma transição ilegal engolida produz um plano que discorda da
#: trajetória e nenhum jeito de dizer qual está certo.
_LEGAL: Mapping[TodoStatus, frozenset[TodoStatus]] = {
    TodoStatus.PENDING: frozenset({ACTIVE, BLOCKED, SKIPPED}),
    TodoStatus.ACTIVE:  frozenset({DONE, FAILED, BLOCKED, PENDING}),
    TodoStatus.BLOCKED: frozenset({PENDING, ACTIVE, SKIPPED, FAILED}),
    TodoStatus.FAILED:  frozenset({PENDING, SKIPPED}),
    TodoStatus.DONE:    frozenset({PENDING}),   # reaberto em regressão
    TodoStatus.SKIPPED: frozenset({PENDING}),
}
```

**A regra que fecha o anti-padrão §58:**

```python
        # §24: conclusão é uma alegação de evidência, então precisa carregar uma.
        if status is TodoStatus.DONE and not (evidence or item.evidence):
            raise TodoTransitionError(
                f"todo {identifier!r} cannot be completed without evidence; "
                f"a model's assertion of success is not verification")
```

Prontidão por dependência:

```python
    def ready(self) -> tuple[TodoItem, ...]:
        """PENDING cujas dependências estão todas DONE ou SKIPPED."""
        settled = {TodoStatus.DONE, TodoStatus.SKIPPED}
        return tuple(item for item in self.items()
                     if item.status is TodoStatus.PENDING
                     and all(self._items[d].status in settled for d in item.dependencies))

    @classmethod
    def from_steps(cls, steps, *, chain: bool = True) -> "TodoManager":
        """Constrói cadeia linear a partir dos passos do planner.

        Encadeado por padrão: passos de um plano são ordinariamente sequenciais,
        e uma lista paralela-por-padrão deixaria o worker aplicar patch antes de
        ter localizado."""
```

Durabilidade para checkpoint/resume:

```python
    @classmethod
    def from_canonical_dict(cls, raw) -> "TodoManager":
        """Reconstrói de um checkpoint. Ignora checagem de transição por
        DESIGN: um estado persistido já é produto de transições legais."""
```

**Verificado:**

```
t1 reproduce failure
after t1: t2 {'total': 4, 'counts': {'done': 1, 'pending': 3}, 'fraction': 0.25}
REFUSED: illegal transition pending -> done for todo 't2'
[x] t1. reproduce failure
[ ] t2. localize owner
[ ] t3. patch
[ ] t4. run tests
```

---

### 8.2 NOVO — `vanguard/packages/apps/coding_max/planning/planner.py` (302 linhas)

Determinístico e por template. Plano autorado por modelo é suportado (`Plan.from_mapping`) mas **não exigido**: para um `test_failure` o plano é sempre "reproduz, localiza, corrige, verifica", e pagar um modelo forte para redescobrir isso é desperdício (§6).

```python
@dataclass(frozen=True, slots=True)
class Plan:
    objective: str
    assumptions: tuple[str, ...] = ()
    steps: tuple[str, ...] = ()
    verification_strategy: tuple[str, ...] = ()
    risk_points: tuple[str, ...] = ()
    revision: int = 0
    reason: str = "initial"

    def to_todos(self) -> TodoManager:
        return TodoManager.from_steps(self.steps)

    @classmethod
    def from_mapping(cls, raw, *, objective="") -> "Plan":
        """Parseia plano autorado por modelo. Parseado, nunca cast (postura CT-03)."""
        steps = tuple(str(s) for s in (raw.get("steps") or ()) if str(s).strip())
        if not steps:
            raise ValueError("a plan must contain at least one step")
        ...
```

Templates por tipo (o exemplo trabalhado do §15 é a linha `complex_bug`):

```python
_TEMPLATES: Mapping[TaskType, tuple[str, ...]] = {
    TaskType.COMPLEX_BUG: (
        "Reproduce the reported failure deterministically",
        "Identify the implementation owner of the failing behaviour",
        "Inspect related tests and existing invariants",
        "Form and record a hypothesis with its falsifier",
        "Apply a minimal scoped patch",
        "Run targeted tests",
        "Inspect the diff for interface changes and run related tests",
    ),
    TaskType.TEST_FAILURE: (
        "Run the failing test and capture the exact failure output",
        "Read the failing assertion and the code under test",
        "Form a hypothesis for the defect and name the owning file",
        "Apply a minimal patch to the implementation",
        "Re-run the targeted test",
        "Run related tests to check for regression",
    ),
    TaskType.MULTI_FILE_FEATURE: (
        "Build a repository map of the affected subsystems",
        "Enumerate every call site and integration point",
        "Establish a green baseline",
        "Implement the core behaviour in its owning module",
        "Wire the behaviour through each integration point",
        "Add tests covering the seams",
        "Run targeted, related, and broader test sets",
    ),
    # ... SIMPLE_FIX, REFACTOR, FEATURE, DEPENDENCY_ISSUE,
    #     REPOSITORY_EXPLORATION, GREENFIELD, LONG_TASK
}
```

Riscos derivados de fato observado, não de opinião:

```python
        risks: list[str] = []
        if profile.uncertainty > 0.6:
            risks.append("Localisation is uncertain; expect to revise the target file")
        if profile.repo_familiarity < 0.4:
            risks.append("Repository is unfamiliar; conventions must be read, not assumed")
        if getattr(repo_map, "dirty", False):
            risks.append("Working tree is dirty; baseline may not be green")
```

### 8.3 Replanning (§17)

```python
class ReplanTrigger(str, Enum):
    """Cada gatilho nomeia uma OBSERVAÇÃO, não um humor."""
    FAILED_ASSUMPTION = "failed_assumption"
    WRONG_LOCALIZATION = "wrong_localization"
    UNEXPECTED_DEPENDENCY = "unexpected_dependency"
    REPEATED_FAILED_PATCH = "repeated_failed_patch"
    UNEXPECTED_TEST_BEHAVIOR = "unexpected_test_behavior"
    MAJOR_CONTEXT_DISCOVERY = "major_context_discovery"
    BUDGET_PRESSURE = "budget_pressure"


class Replanner:
    """Revisa um plano em resposta a evidência (§17).

    Revisão é ADITIVA quando possível. Descartar o plano inteiro na primeira
    contradição joga fora os passos que já produziram evidência, e re-derivá-los
    custa turnos que o budget não tem."""

    _INSERTIONS: Mapping[ReplanTrigger, tuple[str, ...]] = {
        ReplanTrigger.WRONG_LOCALIZATION: (
            "Widen the repository search with different terms and symbol lookup",
            "Re-identify the owning file from fresh evidence"),
        ReplanTrigger.REPEATED_FAILED_PATCH: (
            "Roll back to the last verified state",
            "Re-read the target at current HEAD before re-patching"),
        ReplanTrigger.UNEXPECTED_DEPENDENCY: (
            "Map the dependency edges around the target",
            "Extend the patch scope to cover the affected callers"),
        # ...
    }
```

Modo de conclusão encolhe em vez de crescer (§42):

```python
        if trigger is ReplanTrigger.BUDGET_PRESSURE:
            steps = insertions + tuple(s for s in remaining
                if "broader" not in s.lower() and "speculative" not in s.lower())
        else:
            steps = insertions + remaining

        if trigger is ReplanTrigger.FAILED_ASSUMPTION and assumptions:
            # A premissa falsificada é DESCARTADA, não silenciosamente mantida —
            # um plano que ainda afirma premissa refutada continuará produzindo
            # o mesmo passo errado.
            assumptions = assumptions[1:]
```

**Verificado:**

```
# Plan (rev 0): fix failing tests
## Assumptions (falsify these first)
  - The change belongs in one of: test_x.py
## Steps
  1. Run the failing test and capture the exact failure output
  ...
REV 1 wrong_localization -> ('Widen the repository search with different terms
                             and symbol lookup', 'Re-identify the owning file...')
TODOS: ['t1','t2','t3','t4','t5','t6']
```

---

## Cap. 9 — Estado ao fim da Wave 2

| Item CM | Estado |
|---|---|
| CM-03 contexto progressivo | ✅ |
| CM-04 TODO/planner | ✅ |
| CM-08 cache de contexto | ✅ (entregue na Wave 1, `IntelligenceCache`) |

**Continua na Wave 3:** verificação em camadas (CM-05), failure classifier (CM-06), recuperação adaptativa (CM-07), model router (CM-09).
