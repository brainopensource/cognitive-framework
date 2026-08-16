# Developer C — port activation bundles

Tickets: `S3-DC-001..003` · Contract: `REQ-PORT-002`, `REQ-PORT-004`, `REQ-PORT-005`

Land each port only as the ICD activation bundle: interface in `vanguard/packages/ports/`, fake in `adapters/`, shared suite in `test/contracts/`. No live network. No OpenRouter (that is `S4-DC-001` / `REQ-PORT-006`).

`ModelPort`: cassette/fake propose; typed instrument errors.  
`EvaluatorPort`: fake verdicts; agency must not import it.  
`SandboxRunner`: fake visibly marked non-contained; unverified report blocks publication.

Must not implement the episode loop or kernel changes.
