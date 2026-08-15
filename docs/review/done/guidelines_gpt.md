## Direct answer

Yes: v4, Rev1 and Rev2 are highly useful for a holistic MVP, but they must not be merged into one larger specification. Use **v4 as the library of safety, evidence and failure-semantics contracts; Rev1 as the systems-level expansion identifying the artifact graph, correction signal, two clocks, metacognition and harness packaging; and Rev2 as the architectural correction that removes premature ontology, over-centralization and statistical rigidity**. Their synthesis should be an executable systems model—a traceable chain from requirement → contract → component → test → metric → evidence—not another vision document. The engineering principle is: **minimal in depth, complete in topology**. The MVP represents every permanent function of the future system, but initially implements only one narrow, integrated capability through each function.

## 1. What each document becomes

| Source                        | Role going forward                                                                                                | Authority                                   |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| **Vanguard v4**               | Repository of candidate invariants, security contracts, event semantics, failure states and evaluation doctrine   | Only explicitly activated rules are binding |
| **Rev1**                      | Holistic systems model and gap analysis: artifact graph, correction records, two clocks, metacognition, packaging | Design input                                |
| **Rev2**                      | Independent simplification, product architecture, generalized statistics, security qualifications and roadmap     | Design input                                |
| **Development Blueprint**     | Integrated architecture, dependency model, capability roadmap, workstreams and milestone gates                    | Governs the program                         |
| **Phase Active Contract**     | Small subset of contracts required by the current integrated spiral                                               | Governs current implementation              |
| **ADR and experiment ledger** | Alternatives, predictions, evidence and reversal decisions                                                        | Governs architectural evolution             |

Do not rewrite all v4 documents before coding. Extract the active contracts, implement them, and revise the larger corpus from integration evidence.

## 2. Translate the nature analogy into an executable composition model

The biological analogy is useful as a model of **composition and emergence**, but the implementation must use typed contracts rather than biological terminology.

| Conceptual level      | Engineering realization                                                                                    |
| --------------------- | ---------------------------------------------------------------------------------------------------------- |
| **Atoms**             | Typed effects and capabilities: read resource, write resource, invoke model, execute process, send request |
| **Molecules**         | Tools and operators composed from effects: search, patch, test, browse, retrieve                           |
| **Polymers**          | Skills, methodologies, workflows and reusable problem-solving strategies                                   |
| **Cells**             | Agents: model + resolved context + tools + memory + policy + budget + goal                                 |
| **Tissues/organs**    | Coordinated agent teams and specialized services                                                           |
| **Organism**          | A complete harness executing a mission under one lifecycle                                                 |
| **Society/ecosystem** | Multiple harnesses, environments, evaluators and users exchanging evidence and artifacts                   |

The important correction is that a tool is not the lowest-level atom: shell, browser and Git are already complex authorities. The true atoms are resource-scoped effects. This lets higher-order structures emerge through composition without giving every component unrestricted power.

## 3. The spine

A theoretically broad problem-solving substrate needs the following permanent functions. They should exist in the MVP even when their first implementations are deliberately narrow.

| Spine component                     | Universal function                                                 | MVP implementation                                                        | Expansion path                                                                |
| ----------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Identity and protocol contracts** | Define episodes, actors, artifacts, messages, effects and evidence | Versioned minimal schemas                                                 | Multiple languages, nodes, organizations and domains                          |
| **Lifecycle coordinator**           | Scheduling, budgets, cancellation, branching and recovery          | One durable episode state machine                                         | Long-running missions, distributed actors and hierarchical budgets            |
| **Event ledger**                    | Experience, causality and state reconstruction                     | Transactional append log plus content-addressed blobs                     | Distributed storage, projections, counterfactual experiments                  |
| **Artifact graph**                  | Heredity and mutable competence                                    | Prompts, tools, context policies and harness manifests                    | Skills, routing, agent teams, memory procedures and harness code              |
| **Capability kernel**               | Authority, containment and resource ownership                      | Resource-scoped grants and sandbox broker                                 | Networks, devices, external organizations and delegated authority             |
| **Observation adapters**            | Perception and sensors                                             | Filesystem, Git, process output and user input                            | Browser, APIs, databases, telemetry, robots and scientific instruments        |
| **Model gateway**                   | Cognitive engines                                                  | One real provider and deterministic fake model                            | Model routing, ensembles, specialist models and local inference               |
| **Context compiler**                | Working consciousness and attention allocation                     | Goal, instructions, repository map, selected files, tools and budget      | Retrieval, compression, salience, personalized and multi-agent context        |
| **Memory system**                   | Short- and long-term retention                                     | Working state plus immutable episodic history                             | Semantic consolidation, procedural memory, forgetting and conflict resolution |
| **Tool runtime**                    | Action on environments                                             | Typed read, search, patch and test tools; restricted shell fallback       | Browser, research, communication, coding, simulation and physical interfaces  |
| **Evaluator/judge**                 | Reality testing and selection                                      | External deterministic tests and policy checks                            | Sealed suites, human adjudication, domain evaluators and meta-evaluation      |
| **Metacognitive record**            | Estimate competence and regulate effort                            | Prior success estimate, uncertainty, abstention and outcome scoring       | Calibrated routing, EV-gated search and autonomous escalation                 |
| **Communication fabric**            | Social coordination                                                | Typed actor messages with identity, budget and provenance                 | Agent teams, organizations, marketplaces and distributed missions             |
| **Optimizer and release authority** | Learning and controlled adaptation                                 | Present as interfaces; no autonomous promotion initially                  | Candidate generation, Pareto archive, canaries, promotion and rollback        |
| **Interaction layer**               | Human intent, supervision and correction                           | CLI, streaming, approval, inspection, cancellation and `CorrectionRecord` | IDE, voice, visual interfaces, remote operation and collaborative control     |

This is the holistic MVP: all future organs have attachment points, identities and evidence semantics, but only the coding path is initially deep.

## 4. Code architecture

Start as a **modular monolith with enforced internal boundaries**, plus separate processes only where trust requires them:

| Module          | Dependency rule                                                        |
| --------------- | ---------------------------------------------------------------------- |
| **contracts**   | Depends on nothing domain-specific                                     |
| **kernel**      | Depends only on contracts and minimal audited libraries                |
| **ledger**      | Implements event/artifact persistence without knowing coding or models |
| **runtime**     | Coordinates episodes through contracts                                 |
| **artifacts**   | Resolves immutable harness manifests and component graphs              |
| **models**      | Provider adapters behind the model gateway                             |
| **context**     | Compiles context from registered sources                               |
| **worker**      | Executes authorized effects inside containment                         |
| **evaluators**  | Separately identified and unreachable from candidate workspaces        |
| **interaction** | CLI/API clients of the runtime                                         |
| **adapters**    | Git, filesystem, shell, browser, databases and future environments     |
| **optimizer**   | Offline candidate generation; initially disabled from promotion        |
| **projections** | Traces, metrics, search indexes, audits and dashboards                 |

A strong implementation baseline would be a memory-safe compiled core—Rust is a reasonable choice for the coordinator, broker, ledger and worker supervision—with TypeScript and Python SDKs and out-of-process adapters. Use SQLite WAL and content-addressed filesystem blobs initially; retain a versioned event envelope so storage can migrate later. Avoid distributed infrastructure until scaling or trust boundaries require it.

## 5. The first complete execution path

The first integrated episode should already exercise the future architecture:

1. The user submits a task.
2. The runtime creates an episode and snapshots the environment.
3. The artifact resolver freezes one harness manifest.
4. The context compiler creates the working context.
5. The model proposes a typed effect.
6. The capability broker authorizes, denies or requests approval.
7. The sandboxed worker executes it.
8. The ledger records the proposal, decision, receipt and resulting artifacts.
9. The state reducer advances the episode.
10. The external evaluator checks the result.
11. The user accepts or corrects the patch.
12. The system records the correction, latency, cost, confidence and outcome.

That thin path already contains perception, cognition, action, memory, judgment, metacognition and human feedback. Future capabilities expand individual stages rather than bypassing them.

## 6. Concurrent development model

Do not build these subsystems sequentially. Establish parallel workstreams behind the shared contracts:

* **Substrate and security:** capabilities, sandbox, lifecycle and fault recovery.
* **Runtime and cognition:** coordinator, model gateway, context compiler and operators.
* **Evidence and evaluation:** ledger, test runner, metrics, corrections and sealed evaluation.
* **Artifact and evolution:** artifact graph, manifests, provenance and candidate workspaces.
* **Product:** CLI, streaming, approvals, inspection, Git workflow and latency.
* **Environments:** coding adapter plus a thin second-domain conformance adapter.
* **Research:** memory, metacognition, evaluation science and improvement experiments.
* **Integration architecture:** interface control, dependency structure matrix, performance budgets and continuous system integration.

Run two-week implementation sprints inside larger integrated spirals. Every sprint must end with a working end-to-end system, even if several components are still simplistic. Every spiral ends with system-level trade studies and may revise contracts.

## 7. Integrated spirals from zero to self-hosting

### Spiral 0 — Executable architecture

Produce the minimal contracts, repository structure, fake model, fake tools, event store, artifact identity, episode reducer and automated architecture tests. Prove that domain adapters cannot depend backward into the kernel.

### Spiral 1 — Trustworthy coding skeleton

Add the real provider, Git workspace, typed coding tools, sandbox, capability broker, recovery, external evaluator and CLI. Fix real repository issues while measuring latency and correction burden.

### Spiral 2 — Holistic Vanguard Alpha

Add harness manifests, working and episodic memory, context compiler versions, correction records, prior competence estimates, actor messaging and a thin second environment. This proves the topology can grow without modifying the kernel.

### Spiral 3 — Evidence laboratory

Add A/A measurement, internal held-out tasks, sealed evaluation, mutation and adversarial tests, evaluator–deployment correlation, canaries and rollback. Vanguard now knows whether an apparent improvement is distinguishable from noise.

### Spiral 4 — Singularity Beta

Use Vanguard daily to modify Vanguard. The offline optimizer may propose changes to prompts, skills, tool descriptions, retrieval or context policy. Every proposal includes a prediction and passes paired evaluation against the incumbent; only the external release authority can promote it. This is the first controlled self-improvement loop.

### Spiral 5 — Cumulative competence

Introduce semantic and procedural consolidation, scoped competence, forgetting, drift invalidation, model-aware artifact expiry and adaptive effort allocation. These are derived from artifacts and failures actually observed during Beta.

### Spiral 6 — General task-solving expansion

Add real non-coding environments through observation, effect and evaluator adapters. Measure which cognition and competence artifacts transfer. Agent teams, research, browsing, communication and other capabilities grow through manifests and artifact composition, not kernel changes.

## 8. Rules that prevent coupling and architectural decay

1. The kernel cannot import models, Git, browsers, memory implementations or domain concepts.
2. Every run resolves immutable versions of every active component.
3. Extensions register through versioned manifests and freeze per episode.
4. Privileged effects cross one broker and one OS-enforced workload boundary.
5. Model output proposes authority but never possesses it.
6. Raw events are preserved; indexes, memories, metrics and dashboards are rebuildable projections.
7. Every model-compensation component declares the deficiency it addresses and when it must be retested.
8. Every interface has contract, compatibility, property and failure-injection tests.
9. Architecture fitness tests enforce dependency direction, kernel size, schema compatibility and latency budgets.
10. Safety checks stay on the fast clock; evaluation, learning and governance stay on the slow clock.
11. New domains add adapters and evaluators, not conditionals in the episode engine.
12. Emergent behavior can propose new artifacts; it cannot modify the judge, authority root or promotion policy.

## Final call

Build Vanguard as a **complete but shallow cognitive substrate first, then deepen it through evidence**. The MVP is not a toy coding script and not a prematurely complete AGI: it is the smallest integrated system containing the stable mechanics required for perception, action, lifecycle, experience, memory, judgment, metacognition, communication and controlled adaptation. Coding is the first deep vertical because it provides the cheapest authoritative evaluator. Once that system fixes real work, records exactly why it succeeded or failed, and can safely compare candidate components against incumbents, Vanguard can begin using itself to improve itself; the resulting artifacts—not biological analogy or speculative documents—will determine the architecture of higher-order agents, teams, memory, cognition and eventually broader problem-solving ecosystems.
