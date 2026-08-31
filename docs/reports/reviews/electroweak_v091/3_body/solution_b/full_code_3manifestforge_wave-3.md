# full_code_3manifestforge — Wave 3
## Verificação em Camadas (CM-05), Failure Classifier (CM-06), Recuperação (CM-07), Model Router (CM-09)

---

## Cap. 10 — Pipeline de verificação

### 10.1 NOVO — `vanguard/packages/apps/coding_max/verification/pipeline.py` (324 linhas)

O contrato que este módulo existe para impor é o §24: *"Uma tarefa não pode ser declarada bem-sucedida meramente porque o modelo diz que está resolvida."*

Todo `CheckResult` carrega o comando que o produziu e o exit code. Uma camada sem comando e sem exit code **não pode** reportar `passed=True`.

```python
class Layer(str, Enum):
    """Escada §23, mais barato primeiro."""
    V1_SYNTAX="V1_syntax";                V2_FORMAT="V2_format"
    V3_LINT="V3_lint";                    V4_TYPECHECK="V4_typecheck"
    V5_TARGETED_TESTS="V5_targeted_tests"; V6_RELATED_TESTS="V6_related_tests"
    V7_BROADER_TESTS="V7_broader_tests";  V8_TASK_VERIFICATION="V8_task_verification"
    V9_PATCH_REVIEW="V9_patch_review"


class VerificationScope(str, Enum):
    TINY_PATCH="tiny_patch"; CANDIDATE="candidate_solution"; FINAL="final_solution"


#: Tabela de política do §23.
_LAYERS_FOR: Mapping[VerificationScope, tuple[Layer, ...]] = {
    VerificationScope.TINY_PATCH: (Layer.V1_SYNTAX, Layer.V5_TARGETED_TESTS),
    VerificationScope.CANDIDATE:  (Layer.V1_SYNTAX, Layer.V3_LINT,
                                   Layer.V5_TARGETED_TESTS, Layer.V6_RELATED_TESTS),
    VerificationScope.FINAL:      (Layer.V1_SYNTAX, Layer.V3_LINT, Layer.V4_TYPECHECK,
                                   Layer.V5_TARGETED_TESTS, Layer.V6_RELATED_TESTS,
                                   Layer.V7_BROADER_TESTS, Layer.V8_TASK_VERIFICATION),
}
```

**O predicado anti-fraude:**

```python
@dataclass(frozen=True, slots=True)
class CheckResult:
    layer: Layer
    passed: bool
    command: str = ""
    exit_code: int | None = None
    stdout_tail: str = ""
    stderr_tail: str = ""
    duration_ms: int = 0
    skipped: bool = False
    skip_reason: str = ""

    @property
    def is_evidence(self) -> bool:
        """Se este resultado pode sustentar uma alegação de sucesso.

        Uma camada pulada, ou que nunca rodou comando, não prova nada. Esta é a
        guarda contra o "fake test results" do §58."""
        return not self.skipped and self.exit_code is not None
```

Isso se propaga ao veredito:

```python
        failures = tuple(c for c in checks if not c.passed and not c.skipped)
        evidential = [c for c in checks if c.is_evidence]
        passed = not failures and bool(evidential)   # <- exige evidência POSITIVA
```

Confiança rastreia **evidência produzida**, não camadas tentadas:

```python
    @staticmethod
    def _confidence(checks, scope) -> float:
        """Camadas puladas não contribuem. Isso impede um run que pulou todo
        teste de reportar alta confiança porque nada falhou."""
        evidential = [c for c in checks if c.is_evidence]
        if not evidential:
            return 0.0
        base = sum(1 for c in evidential if c.passed) / len(evidential)
        weight = {TINY_PATCH: 0.6, CANDIDATE: 0.8, FINAL: 1.0}[scope]
        ran_tests = any(c.layer in (V5, V6, V7) for c in evidential)
        return round(base * weight * (1.0 if ran_tests else 0.5), 4)
```

Parada no primeiro erro duro:

```python
            # Para na primeira falha dura: camadas posteriores reportariam ruído
            # em cascata, e o classifier só precisa da primeira causa.
            if not check.passed and not check.skipped:
                break
```

Ferramenta ausente não é falha de tarefa:

```python
        # Uma ferramenta opcional ausente NÃO é falha de tarefa. Reportá-la como
        # tal faria a disponibilidade do lint decidir resultado de tarefa.
        if tolerate_missing and exit_code != 0 and _tool_missing(stdout, stderr):
            return CheckResult(layer=layer, passed=True, skipped=True,
                               command=command, skip_reason="tool not installed")
```

Runner injetável — em produção, roteia pelo `proc.exec` autorizado pelo kernel (§40):

```python
    def __init__(self, root, *, runner: Callable[[str,int],tuple[int,str,str]] | None = None,
                 test_command="python -m pytest", lint_command="python -m ruff check",
                 typecheck_command="python -m mypy", timeout_s=600):
        """O runner é injetável para que o harness roteie execução pelo adapter
        `proc.exec` autorizado pelo kernel em vez de chamar direto. O runner
        direto padrão existe para avaliação offline do próprio pipeline;
        composição de produção fornece o runner autorizado (§40: adaptadores
        executam, políticas autorizam)."""
```

Pressão de budget corta para o essencial (§42):

```python
    if budget_pressure:
        # Modo conclusão: mantém só o que pode FALSIFICAR a alegação.
        layers = [l for l in layers if l in
                  (Layer.V1_SYNTAX, Layer.V5_TARGETED_TESTS, Layer.V8_TASK_VERIFICATION)]
```

**Verificado no repo real:**

```
passed True conf 0.3
  V1_syntax          True  exit=0
  V5_targeted_tests  True  skip  "no tests mapped to the changed target"

layers FINAL:          ['V1_syntax','V3_lint','V4_typecheck','V5_targeted_tests',
                        'V6_related_tests','V7_broader_tests','V8_task_verification']
layers budget_pressure:['V1_syntax','V5_targeted_tests','V8_task_verification']
```

> Confiança **0.3**, não 1.0, porque nenhum teste realmente rodou. É exatamente o comportamento pedido: sintaxe passar não é evidência de correção.

---

## Cap. 11 — Taxonomia e classificação de falhas

### 11.1 NOVO — `vanguard/packages/apps/coding_max/recovery/failures.py` (217 linhas)

Determinístico e dirigido por evidência. Lê saída de verificação, trajetória e estado do repositório — **nunca** o relato do próprio modelo sobre o que deu errado, que é o mais provável de estar confiantemente errado.

```python
class FailureClass(str, Enum):
    """Taxonomia §25, literal."""
    TASK_MISUNDERSTOOD; WRONG_FILE; INSUFFICIENT_CONTEXT; EXCESSIVE_CONTEXT
    WRONG_HYPOTHESIS; BAD_PATCH; INCOMPLETE_PATCH; TEST_FAILURE; REGRESSION
    TOOL_FAILURE; ENVIRONMENT_FAILURE; REPEATED_REASONING_FAILURE
    STALE_MEMORY; BUDGET_PRESSURE; NONE


@dataclass(frozen=True, slots=True)
class TrajectorySignals:
    """O que o classifier pode saber. Tudo é fato OBSERVADO."""
    turns_used: int = 0
    turns_remaining: int = 0
    repeated_proposal_digests: int = 0
    distinct_files_edited: int = 0
    patch_apply_failures: int = 0
    tool_errors: int = 0
    consecutive_failed_verifications: int = 0
    search_hits_last: int = 0
    context_tokens: int = 0
    context_budget: int = 1
    previously_passing_now_failing: int = 0
    edited_paths: tuple[str, ...] = ()
    plan_revisions: int = 0
```

**Ordem importa** — classes estruturais antes de parsing de texto:

```python
        # Classes ESTRUTURAIS, checadas antes de qualquer parsing de saída.
        # Descrevem a FORMA da trajetória e são mais confiáveis que texto de log,
        # que frequentemente reporta sintoma de causa anterior.

        if signals.budget_fraction_left < 0.15 and signals.turns_used > 0:
            return FailureVerdict(FailureClass.BUDGET_PRESSURE, 0.9, ...)

        if signals.repeated_proposal_digests >= 2:
            return FailureVerdict(FailureClass.REPEATED_REASONING_FAILURE, 0.85,
                "the same proposal was produced repeatedly, so retrying it "
                "unchanged cannot produce a different result", ...)

        if signals.patch_apply_failures >= 2:
            return FailureVerdict(FailureClass.STALE_MEMORY, 0.75,
                "repeated patch-application failures indicate the context "
                "no longer matches the file on disk", ...)

        if signals.previously_passing_now_failing > 0:
            return FailureVerdict(FailureClass.REGRESSION, 0.9, ...)
```

Padrões sobre stderr/stdout capturado:

```python
_PATTERNS: tuple[tuple[str, FailureClass, str], ...] = (
    (r"no module named|importerror|modulenotfounderror", ENVIRONMENT_FAILURE, ...),
    (r"command not found|no such file or directory|permission denied", ENVIRONMENT_FAILURE, ...),
    (r"syntaxerror|indentationerror|unexpected token|parse error", BAD_PATCH,
     "the patch left the file unparseable"),
    (r"patch does not apply|hunk failed|corrupt patch|context mismatch", BAD_PATCH, ...),
    (r"timeout|timed out|killed", ENVIRONMENT_FAILURE, ...),
    (r"attributeerror|nameerror|typeerror.*not defined", INCOMPLETE_PATCH,
     "the change referenced something that does not exist"),
    (r"assertionerror|assert ", TEST_FAILURE, "an assertion failed"),
)
```

Desambiguação importante:

```python
                # Um teste falhando SEM edições ainda não é problema de patch;
                # é o passo de reprodução funcionando como pretendido.
                if (failure_class is FailureClass.TEST_FAILURE
                        and signals.distinct_files_edited == 0):
                    return FailureVerdict(FailureClass.WRONG_HYPOTHESIS, 0.6,
                        "a test fails but nothing has been edited, so no "
                        "hypothesis has been tested yet", (pattern,))
```

**Verificado:**

```
turns 9/1                        -> BUDGET_PRESSURE
repeated_proposal_digests=3      -> REPEATED_REASONING_FAILURE
previously_passing_now_failing=2 -> REGRESSION
search_hits_last=0, edits=0      -> INSUFFICIENT_CONTEXT
```

---

## Cap. 12 — Estratégias de recuperação e budget de retry

### 12.1 NOVO — `vanguard/packages/apps/coding_max/recovery/policy.py` (222 linhas)

O §26 fecha com a regra que este módulo impõe **mecanicamente**: *"Todo retry deve mudar o estado ou a estratégia."*

```python
class RecoveryAction(str, Enum):
    EXPAND_SEARCH; RETRIEVE_MISSING; COMPRESS_CONTEXT; REFRESH_CONTEXT
    ROLLBACK_AND_REVIEW; ANALYZE_TEST_FAILURE; REPLAN; ESCALATE_MODEL
    RETRY_TOOL; SWITCH_TOOL; NARROW_PATCH_SCOPE; WIDEN_PATCH_SCOPE
    ENTER_COMPLETION_MODE; ABANDON


#: Mapeamento §26, estendido a TODA classe da taxonomia.
_ACTIONS_FOR: Mapping[FailureClass, tuple[RecoveryAction, ...]] = {
    WRONG_FILE:                (EXPAND_SEARCH, REPLAN),
    INSUFFICIENT_CONTEXT:      (RETRIEVE_MISSING, EXPAND_SEARCH),
    EXCESSIVE_CONTEXT:         (COMPRESS_CONTEXT,),
    BAD_PATCH:                 (ROLLBACK_AND_REVIEW, NARROW_PATCH_SCOPE),
    INCOMPLETE_PATCH:          (WIDEN_PATCH_SCOPE, RETRIEVE_MISSING),
    TEST_FAILURE:              (ANALYZE_TEST_FAILURE, REPLAN),
    REGRESSION:                (ROLLBACK_AND_REVIEW, NARROW_PATCH_SCOPE),
    WRONG_HYPOTHESIS:          (REPLAN, EXPAND_SEARCH),
    TASK_MISUNDERSTOOD:        (REPLAN, ESCALATE_MODEL),
    REPEATED_REASONING_FAILURE:(ESCALATE_MODEL, REPLAN),
    TOOL_FAILURE:              (RETRY_TOOL, SWITCH_TOOL),
    ENVIRONMENT_FAILURE:       (SWITCH_TOOL, REPLAN),
    STALE_MEMORY:              (REFRESH_CONTEXT,),
    BUDGET_PRESSURE:           (ENTER_COMPLETION_MODE,),
    NONE:                      (),
}
```

**Ponto arquitetural crítico** — cada ação vira uma diretiva que o substrato já conhece:

```python
#: Qual `StrategyDirective` kind carrega cada ação ao runtime. Os kinds são
#: FIXOS por `ports/meta_controller.py::DIRECTIVE_KINDS`; nada aqui pode
#: inventar um — é isso que mantém isto um plugin de política.
_DIRECTIVE_FOR: Mapping[RecoveryAction, str] = {
    EXPAND_SEARCH: "request_context";      RETRIEVE_MISSING: "request_context"
    COMPRESS_CONTEXT: "request_context";   REFRESH_CONTEXT: "request_context"
    ROLLBACK_AND_REVIEW: "delegate";       ANALYZE_TEST_FAILURE: "change_verification"
    REPLAN: "revise_plan";                 ESCALATE_MODEL: "retry"
    RETRY_TOOL: "retry";                   SWITCH_TOOL: "redirect"
    NARROW_PATCH_SCOPE: "revise_plan";     WIDEN_PATCH_SCOPE: "revise_plan"
    ENTER_COMPLETION_MODE: "conclude";     ABANDON: "stop"
}
```

Budget §27 consumido por **estratégia**, não por contagem de tentativa:

```python
@dataclass
class RetryBudget:
    same_strategy: int = 1
    alternate_strategy: int = 2
    reviewer_escalation: int = 1
    model_escalation: int = 1
```

Seleção que nunca repete estratégia gasta:

```python
        for action in candidates:
            # §26: um retry que repete estratégia gasta não é recuperação, então
            # uma ação já tentada é PULADA em vez de reemitida com outro rótulo.
            if action in self._history:
                continue
            if action is RecoveryAction.ESCALATE_MODEL:
                if not can_escalate_model or not self._budget.spend("model_escalation"):
                    continue
            elif action is RecoveryAction.ROLLBACK_AND_REVIEW:
                if not reviewer_available or not self._budget.spend("reviewer_escalation"):
                    continue
            ...
        # Toda estratégia mapeada gasta. Terminar o melhor candidato sob modo de
        # conclusão bate loop, e bate abandonar de vez.
```

**Verificado — a escada completa:**

```
WRONG_FILE                 -> expand_search        kind=request_context  alt=1
WRONG_FILE                 -> replan               kind=revise_plan      alt=0
BAD_PATCH                  -> rollback_and_review  kind=delegate         rev=0
REPEATED_REASONING_FAILURE -> escalate_model       kind=retry            esc=0
BUDGET_PRESSURE            -> enter_completion_mode kind=conclude
```

Nunca repete; escala; entra em modo de conclusão. Sem loop infinito possível.

---

## Cap. 13 — Model router

### 13.1 NOVO — `vanguard/packages/apps/coding_max/routing/router.py` (148 linhas)

Envolve o `RoleAwareRouter`/`TierLadder` existente em vez de substituí-lo. O substrato já é dono de bandas e mecânica de escalação; o que faltava é a **política** que mapeia papel + histórico de falhas → banda.

```python
class CodingRole(str, Enum):
    CLASSIFIER="classifier"; PLANNER="planner"; WORKER="worker"
    REVIEWER="reviewer";     REPLANNER="replanner"; SUMMARIZER="summarizer"


#: Banda padrão por papel. Modelos baratos fazem síntese mecânica; worker e
#: reviewer pegam a banda forte porque é ali que correção é decidida.
#: Classificação está AUSENTE: é determinística e não precisa de modelo.
_DEFAULT_BAND: Mapping[CodingRole, str] = {
    CodingRole.CLASSIFIER: "cheap",   CodingRole.SUMMARIZER: "cheap",
    CodingRole.PLANNER: "mid",        CodingRole.REPLANNER: "mid",
    CodingRole.WORKER: "strong",      CodingRole.REVIEWER: "strong",
}

_LADDER: tuple[str, ...] = ("cheap", "mid", "strong", "frontier")
```

```python
        # Tarefa de alta complexidade começa o worker um degrau acima em vez de
        # descobrir a necessidade depois de duas falhas desperdiçadas.
        if role is CodingRole.WORKER and complexity >= 0.75 and not force_band:
            band = _up(band)

        # §29: escala em falha REPETIDA, nunca na primeira.
        if (previous_failures >= 2 and self._allow_escalation
                and budget_can_escalate and not force_band):
            band = _up(band); escalated = True
```

Degradação em vez de exceção:

```python
    def _model_for(self, band: str) -> str:
        """Primeiro modelo configurado na banda, degradando escada abaixo.

        Degradar em vez de levantar importa: um deployment que configura só duas
        bandas ainda precisa rodar, e uma entrada `frontier` ausente deve
        resolver silenciosamente para a banda mais forte que existe."""
```

**Verificado:**

```
classifier                    -> cheap    gpt-4o-mini
worker (default)              -> strong   claude-opus
worker (complexity 0.85)      -> frontier claude-opus-thinking  "complexity warrants stronger worker"
worker (3 prior failures)     -> frontier claude-opus-thinking  escalated=True
```

---

## Cap. 14 — Estado ao fim da Wave 3

| Item CM | Estado |
|---|---|
| CM-05 pipeline de verificação | ✅ |
| CM-06 failure classifier | ✅ |
| CM-07 recuperação adaptativa | ✅ |
| CM-09 model router / fallback | ✅ |

**Continua na Wave 4:** controller de integração, reviewer condicional, presets, observabilidade, critérios de aceitação.
