# Lane SA Developer Packet — L1–L5 Prefix-Stable Context Compiler

**Assignee:** Lead Software Architect / Principal Tech Lead  
**Tickets:** `S5-SA-001`, `S5-SA-002`, `S5-INT-001`  
**Complexity:** Level 4 / 5 (Gate Component)  
**Contract Row:** [`REQ-CTX-001`](file:///home/rocha/Coding/Aether-D-System/docs/sprint0/active-mvp-contract.json)  
**Owned Code:** `vanguard/packages/agency/context/`  
**Target Test:** `test/agency/test_context_compiler.py`

---

## 1. Scope & Objective
Implement the prefix-stable, layered context compiler in `vanguard/packages/agency/context/compiler.py`.

The compiler transforms task instructions, active tools, repository maps, and rolling interaction history into an ordered, token-budgeted prompt vector:
$$\text{Prompt} = [L1: \text{System Core}] + [L2: \text{Tool Schemas}] + [L3: \text{Repo Map}] + [L4: \text{Task Brief}] + [L5: \text{Rolling Dialogue}]$$

---

## 2. Invariants & Rules
1. **Prefix Immutability ($L1 \to L3$):** Layers $L1$, $L2$, and $L3$ must be byte-for-byte stable across turns to exploit provider KV prompt caching. Dynamic information belongs in $L4$ or $L5$.
2. **Provenance & Budgeting:** Every block carries its source tag and byte length. If total tokens exceed the model window limit, truncate $L5$ (oldest tool results first) using `result_eviction` before compacting $L4$. Never truncate $L1$ or $L2$.
3. **Pre-Action Competence Prior ($S5-SA-002$):** Before emitting Turn 1 to the model, log the prior $P(\text{success} \mid \text{task})$ to the event ledger via `CompetencePriorRecorded`.
4. **Identifier Lint:** Strictly forbid cognitive nouns (`plan`, `reflect`, `debug`, `architect`) as class or method names in `agency/context/`.

---

## 3. First Failing Test & Verification
```bash
python3 -m unittest test.agency.test_context_compiler
python3 tools/check_boundaries.py
```
Must prove: $L1–L3$ hash identity across 10 simulated turns; token truncation preserves system core; prior event persists to event store.
