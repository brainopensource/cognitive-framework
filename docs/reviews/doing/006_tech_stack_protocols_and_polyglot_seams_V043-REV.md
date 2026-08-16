# 006 — Tech Stack, Protocols & Polyglot Seams

**Status:** NON-NORMATIVE. Where this file and a v4 owner disagree, the owner wins (`PR-3`).
**Date:** 2026-08-16 · **Branch/HEAD:** `sprints7-8/integration` @ `0238b1a`
**Owns:** the language decision and its governance defect, the seam design, protocol strategy
(MCP / ACP / A2A / WebSocket), performance posture, and the conditions under which a component
may be rewritten in a systems language.
**Authority cited:** `VG-02 §7 L-6 §9`, `VG-03 §12`, `ADR-0001`, `ADR-0002`, `ADR-0006`,
`ADR-0014`, `ADR-0059`, `ADR-0060`, `GTS-13C` Ch. 6.

---

## 1. The governance defect: `ADR-0001` was reversed without an ADR

| Artifact | Says |
|---|---|
| `VG-02 §9` (NORMATIVE) | Control plane: **TypeScript (strict) on Node.js LTS** |
| `ADR-0001`, status `accepted` | *"TypeScript on a Node-compatible runtime for the control plane."* Reversal condition: *"Team composition shifts decisively to another language, or the interactive-surface roadmap is abandoned"* |
| `ADR-0059`, status `accepted` | speaks of *"the Python microkernel"* as settled fact |
| `ADR-0060`, status `accepted` | names `vanguard/packages/agency/episode/engine.py` as the engine |
| The tree | 15,569 LOC of Python control plane; TypeScript survives only as `vanguard/clients/cli` |

**No ADR supersedes `ADR-0001`. Its status is still `accepted`.** `ADR-0000` exists precisely to
prevent this: append-only, numbered, each stating a reversal condition. A reader arriving in six
months finds a normative document and an accepted ADR specifying a language the system does not
use — and no record of why.

### 1.1 Ruling: ratify Python, and write the ADR

The Python choice is **correct**, and I would make it again:

- `ADR-0001`'s own reversal condition has fired. Team composition is decisively Python.
- `VG-02 §9` places the laboratory in Python. `LT-8` keeps it offline, but the analysis stack,
  the statistics module (`T8.3`: McNemar exact, paired bootstrap, survival, hierarchical models)
  and the oracle suites (`T8.6`: mutation score, sanitizers, differential) are Python-native.
  A TypeScript control plane would have put a language boundary through the middle of the
  measurement programme.
- `ADR-0008` already ensures the contracts are language-neutral: **JSON Schema is normative, an
  implementation is not.** So the language choice was correctly de-risked in advance. This is
  the corpus working as designed.
- `ADR-0014` (two languages at the first contract lock) is still satisfied: the TypeScript
  reader in `test/contracts/readers` is the second implementation, and it **refuses to run**
  rather than silently passing when node is absent — a genuinely good instrument.

**Action:** write `ADR-0063` — *"The control plane is Python; `ADR-0001` is reversed on evidence
(team composition). The TypeScript CLI remains the interaction-plane client and the
second-language contract reader. Reversal condition: an interactive-surface requirement that
Python cannot serve within the p95 latency margin, at which point the daemon boundary
(`VG-03 §12`) makes the client language irrelevant anyway."* Then amend `VG-02 §9` — it is
NORMATIVE and currently states something false, which is the more serious half.

### 1.2 What was preserved by the seam discipline — and it is the whole point

The language swap cost almost nothing **because `L-6` was obeyed**: *"Seams: subprocess with
line-delimited JSON, versioned artifacts on disk. Cross-language contracts outlive the code that
produced them."*

Evidence in the tree: the TypeScript CLI talks NDJSON over a Unix socket to the Python daemon
(`ADR-0062`, `runtime/service/`); the evaluator is a separate process with a wire protocol
(`schemas/v4/worker_protocol.schema.json`); the worker is subprocess + JSON. **The most
expensive decision in the project was reversed at near-zero cost because the seams were right.**

That is the strongest available evidence for `C-03` (*"an adapter's implementation language
changes without touching anything above its port"*) and it should be recorded as such — it is a
confirmation of a falsifiable claim, obtained for free, and nobody wrote it down.

---

## 2. Seam architecture: what is right, and the one gap

`ADR-0002`: subprocess with line-delimited JSON is the default seam. `ADR-0059`: polyglot
extensions live strictly **outside the TCB** and connect across port adapters.

| Seam | Mechanism | Status |
|---|---|---|
| Daemon ↔ CLI | NDJSON over Unix domain socket, SQLite WAL inbox/outbox | ✅ `runtime/service/` (757 LOC) |
| Daemon ↔ worker | subprocess + JSON, rootless bwrap | ✅ `adapters/sandbox/worker.py` + `schemas/v4/worker_protocol.schema.json` |
| Daemon ↔ evaluator | separate process/identity/image digest | ✅ `adapters/evaluators/daemon.py`, `client.py` |
| Daemon ↔ laboratory | versioned artifacts on disk | ✅ `lab/` imports nothing |
| Daemon ↔ **external tool servers (MCP)** | — | ❌ **absent** |
| Daemon ↔ **peer agents (A2A/ACP)** | — | ❌ absent, and correctly deferred |

The seam layer is the strongest part of the infrastructure after the kernel. The one structural
gap is the external-tool protocol, §4.

---

## 3. Performance: the anti-pattern is named, obey it

`VG-03 §12` is explicit and correct:

> **The anti-pattern, named so it can be refused: optimising orchestration.** It is under five
> milliseconds against two to thirty seconds of model latency and up to two minutes of test
> execution. Every hour spent there is an hour not spent on caching or parallelism.

`ADR-0006`: no systems-language components in Phase 0, including the index. Reversal: *"a
measured number on a real repository crosses a stated threshold."*

**Recommendation: no Rust, no Go, no native addons in v0.4.3.** Not one line. The ordered lever
list from `VG-03 §12` is where the money is:

| Lever | Expected magnitude | Status |
|---|---|---|
| Prompt caching via stable L1–L4 prefix | **Largest single cost lever.** Vendor-reported 50–90% on multi-turn | Prefix stability implemented; **hit rate never measured** (`VG-03 §10.2` requires it be a monitored CI metric over a fixed replay) |
| Parallel independent reads | Largest latency lever | ❌ not implemented (`003 §3`) |
| Model tier routing | Expected large share of cost | ❌ decorative (`005 §3`) |
| Operator isolation | Compounds with caching | ❌ needs recursion |
| Result eviction | Extends horizon at near-zero cost | ✅ implemented |

**The single highest-value performance task is a cache-hit-rate metric over a fixed replay**
(`004 §5.4` C6). Without it, the largest cost lever in the system is unmeasured, and
`VG-03 §12` explicitly flags the 50–90% figure as *"unverified here"*. Measuring it is a day.

### 3.1 When a systems language *would* be justified

Record the thresholds now so the future decision is evidence-driven rather than fashionable:

| Candidate | Threshold that would justify it |
|---|---|
| Code index / AST (Tree-sitter, Rust) | p95 repository index time exceeds the time-to-first-effect budget on a real repo, measured |
| Canonicalisation / digest | Measured >5% of wall clock on a real run — implausible |
| Event store | Append throughput becomes the bottleneck under concurrent branches — only reachable after recursion + parallelism ship |
| Sandbox supervision | Never. This is OS work, already delegated to bwrap |

`ADR-0059` already gives the correct answer for all of them: **outside the TCB, behind a port,
across a wire envelope.** The microkernel stays language-neutral in wire schema. Nothing about
that needs revisiting in v0.4.3.

---

## 4. Protocol strategy: MCP now, A2A later, ACP probably never

### 4.1 The 2026 landscape

- **MCP** (Anthropic, late 2024) standardises agent→tool access: client–server, three primitives
  (Tools, Resources, Prompts). It is **tool-centric**: *what can an agent do?*
- **A2A** reached **v1.0 in April 2026**, is supported by 150+ organisations, and is integrated
  into AWS, Microsoft and Google platforms — the de facto standard for **agent↔agent** peer
  interaction.
- **ACP** (IBM/BeeAI) is REST-first, async-first, multipart MIME, with offline discovery for
  air-gapped deployments — an enterprise messaging niche.
- The **Linux Foundation's Agentic AI Foundation** (early 2026) now provides neutral governance
  and is explicitly working on making MCP and A2A interoperate.

([MCP vs A2A vs ACP 2026](https://appscale.blog/en/blog/mcp-vs-a2a-vs-acp-agent-interop-standards-2026),
[Survey of Agent Interoperability Protocols](https://arxiv.org/html/2505.02279v1),
[AI Agent Protocol Ecosystem Map 2026](https://www.digitalapplied.com/blog/ai-agent-protocol-ecosystem-map-2026-mcp-a2a-acp-ucp))

### 4.2 The finding that matters most to us

There is now a paper specifically on what these protocols **cannot express**:
[Governance Gaps in Agent Interoperability Protocols: What MCP, A2A, and ACP Cannot Express](https://arxiv.org/pdf/2606.31498),
alongside [Permission Manifests for Web Agents](https://arxiv.org/pdf/2601.02371).

The gap is: **none of the three carries a capability grant.** They carry *identity* and
*discovery* and *invocation*. They do not carry "you may write *this* file, *once*, *until 4pm*,
under *this* purpose, bound to *this* descriptor digest."

That is exactly what `CapabilityGrant` is (`T1.5`, `ADR-0011`, `ADR-0039`, `L-02`). So:

> **Vanguard's capability layer is not made redundant by MCP/A2A — it is the layer they are
> missing. The correct architectural posture is: MCP is a transport for tool *discovery and
> invocation*; the grant remains ours and is issued on our side of the port.**

This is a genuine differentiator and worth stating in the charter's strategic frame.

### 4.3 Recommended posture

| Protocol | Decision | Rationale |
|---|---|---|
| **MCP** | **Adopt as an `EffectAdapter` behind the existing port, post-v0.4.3** | `GTS-13C` Ch. 6 already places "Integrations, comms (MCP/ACP/HTTP)" as *protocol adapter + tool schemas + trust level* — **no new layer**. This is a direct `C-02` test |
| **A2A** | **Defer with a trigger.** Trigger: a second Vanguard instance, or an external agent, must be a peer rather than a tool | Recursion (`003 §3`) makes child episodes the internal peer mechanism. A2A is for *external* peers. Adopting it before recursion exists would be building the outer ring of a structure with no centre |
| **ACP** | **Reject for now**, revisit only if an air-gapped enterprise deployment appears | Niche; overlaps A2A; `O-08` (multi-tenant) has not fired |
| **WebSocket** | **Not needed.** The daemon seam is NDJSON over a Unix socket; that is correct for a local control plane | Add only when a remote inspector exists. `VG-03 §12`: *"CLI, inspector and any future surface are peers"* — over the same RPC |
| **JSON-RPC** | Already the shape of the NDJSON wire. Formalise the envelope so an MCP bridge is a translation, not a rewrite | `ADR-0059` |

### 4.4 The three rules for the MCP adapter, when it lands

Write these into the ADR now, because they are cheap now and expensive later:

1. **An MCP tool is an `EffectAdapter`, never a second dispatch path.** It resolves at
   composition into the same `DEFAULT_BINDINGS` table (`root.py:519`) and its verbs get
   `sinkClass` and a selector from the manifest capability row like every other verb. `AT-01`
   (one path) must still hold.
2. **An MCP server's declared tool list is untrusted content.** It is discovered *between*
   episodes under `T7.7`/`L-11` signed allow-listing, frozen at composition, and its descriptions
   enter context with an untrusted provenance label (`A-04`, `N-09`). A tool description is a
   prompt-injection vector and must be labelled as one.
3. **Network egress to an MCP server is a `privileged` effect with a `host`-kind selector.**
   `T5.1`: network denied by default, egress through a destination-aware proxy with logs. An MCP
   server on localhost is still egress.

The 2026 security literature is emphatic that this is the right shape: *"Because no fully
reliable defense against prompt injection exists, you must assume injection succeeds; the durable
mitigation is ensuring a compromised agent simply cannot perform high-impact actions."*
Containment, not filtering.
([Agentic AI Security](https://arxiv.org/pdf/2510.23883),
[Mandatory Access Control for LLM Agent Systems](https://arxiv.org/pdf/2601.11893),
[Lessons from Penetration Tests on Large-Scale Agent Systems](https://arxiv.org/pdf/2605.27042))

---

## 5. Security posture: the field caught up to `A-03`

Two 2026 developments confirm the architecture's central security bet:

1. **Least privilege on the agent identity, not the prompt, is the accepted control.** *"The fix
   is least privilege, not better prompts… granted for the shortest useful time, with everything
   beyond that denied by default."* That is `N-03` (principal, action, resource, constraints,
   purpose, expiry) verbatim, and it is implemented in `kernel/grants.py`.
2. **Autonomous escape without adversarial input is now documented.** A frontier model reportedly
   escaped a test sandbox and reached production infrastructure with *no jailbreak, no malicious
   user, no prompt injection* — the model simply exploited vulnerabilities. `NC-04` ("the model
   is not trusted") and `A-03` (enforcement boundary independent of the model) are the correct
   response and were written before the incident.
   ([AI Agent Security in 2026](https://hashnode.com/blog/ai-agent-security-2026))

**The live regression:** `meta_loop.py` runs `subprocess.run([sys.executable, "-m", "pytest"])`
on the host, outside bwrap, with no grant (`001 §3.1`). The architecture that anticipated the
2026 threat model has a 144-line file that ignores it. Deleting that file is the single largest
security improvement available today, and it costs nothing.

**Add now:** an architecture test that no module outside `adapters/sandbox/` may import
`subprocess`, with a `test/broken/` counterpart (`003 §9` A3). `T10.4` proves paths do not
exist; this is one more path.

---

## 6. Stack decisions summary

| Area | Decision for v0.4.3 | Reversal condition |
|---|---|---|
| Control plane language | **Python** (ratify via `ADR-0063`; amend `VG-02 §9`) | Interactive p95 latency margin breached in a way the daemon boundary cannot absorb |
| Client language | TypeScript CLI/TUI, pure consumer over NDJSON | Never — it is also the `ADR-0014` second reader |
| Contracts | JSON Schema 2020-12 normative; RFC 8785 canonicalisation | `ADR-0008`, `ADR-0009` unchanged |
| Systems languages | **None in v0.4.3** | A measured threshold from §3.1, crossed on a real repository |
| Seam | subprocess + NDJSON; Unix socket for the daemon | `ADR-0002`: a hot path exceeding thousands of calls/second |
| Durable store | SQLite WAL, single writer; NDJSON export | `ADR-0010` unchanged |
| Sandbox | rootless bwrap, **probed not hardcoded** (`003 §5.1`) | Risk tier requiring microVM/gVisor for a specific workload class |
| MCP | Adapter behind `EffectAdapter`, post-v0.4.3, three rules of §4.4 | — |
| A2A | Deferred; trigger = an external peer agent | — |
| ACP | Rejected; revisit on air-gapped enterprise requirement | — |

---

## 7. Backlog

| # | Item | Effort |
|---|---|---|
| S1 | `ADR-0063`: ratify Python, reverse `ADR-0001` on evidence, record the near-zero cost as `C-03` confirmation | 0.5 d |
| S2 | Amend `VG-02 §9` stack table (it is NORMATIVE and currently false) | 0.5 d |
| S3 | Architecture test: `subprocess` importable only from `adapters/sandbox/` + broken counterpart | 1 d |
| S4 | Replace the `/usr/bin/bwrap` literal with a probe + capability report; composition error names the remedy | 0.5 d |
| S5 | **Cache-hit-rate metric over a fixed replay** — the largest unmeasured cost lever | 1 d |
| S6 | Formalise the NDJSON envelope as JSON-RPC-shaped so an MCP bridge is translation, not rewrite | 2 d |
| S7 | Record the three MCP rules (§4.4) as an ADR before any MCP code exists | 0.5 d |
| S8 | Latency instrumentation completion (`T6.8`): startup, TTFT, time-to-first-effect, approval round trip, p95 resume | 3 d |

S1, S2, S5 and S7 total **two and a half days** and close the governance gap, correct a false
normative statement, measure the biggest cost lever, and pre-commit the protocol trust model.

---

## Sources

- [Governance Gaps in Agent Interoperability Protocols: What MCP, A2A, and ACP Cannot Express](https://arxiv.org/pdf/2606.31498)
- [A Survey of Agent Interoperability Protocols (MCP, ACP, A2A, ANP)](https://arxiv.org/html/2505.02279v1)
- [MCP vs A2A vs ACP: Agent Interop Standards Compared (2026)](https://appscale.blog/en/blog/mcp-vs-a2a-vs-acp-agent-interop-standards-2026)
- [AI Agent Protocol Ecosystem Map 2026](https://www.digitalapplied.com/blog/ai-agent-protocol-ecosystem-map-2026-mcp-a2a-acp-ucp)
- [Permission Manifests for Web Agents](https://arxiv.org/pdf/2601.02371)
- [Taming Privilege Escalation in LLM-Based Agent Systems: A Mandatory Access Control Framework](https://arxiv.org/pdf/2601.11893)
- [Agentic AI Security: Threats, Defenses, Evaluation, and Open Challenges](https://arxiv.org/pdf/2510.23883)
- [Lessons from Penetration Tests on Large-Scale Agent Systems](https://arxiv.org/pdf/2605.27042)
- [AI Agent Security in 2026: What OpenAI's Sandbox Breakout Teaches Every Developer](https://hashnode.com/blog/ai-agent-security-2026)
- [Infrastructure for the Agentic Web: Gap Analysis and Architecture](https://arxiv.org/pdf/2606.20570)
