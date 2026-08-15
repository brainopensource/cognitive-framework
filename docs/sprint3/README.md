# Sprint 3 developer packet index

Project decision: `CONDITIONAL GO — local implementation; no merge to main until DECISION-0003 close conditions`  
Decisions: `DECISION-0003`, `ADR-0055`, `ADR-0056` · 2026-08-15

Sprint 3 does **not** contain T2.6–T3.8 (already covered). Four lanes start day one against merged kernel/ledger. Integration is `S3-INT` in the last 2–3 days, owned by Senior A.

| Developer | Lane | Packet | Cx | Contract |
|---|---|---|---|---|
| Senior A | S3-SA | `sa-packet.md` | 4 GATE | `REQ-EXEC-001` |
| Senior B | S3-SB | `sb-packet.md` | 4 GATE | `REQ-EXEC-002` |
| Developer C | S3-DC | `dc-packet.md` | 2 FAST | `REQ-PORT-002..005` |
| Developer D | S3-DD | `dd-packet.md` | 2 FAST | `REQ-HARN-001`, `REQ-PORT-003` fake |

Do not implement OpenRouter, worker OS isolation, trust-spine demo, or delete `slice/` in this sprint. Do not import `spike/` or `slice/`.

## Required reading

1. Decision Record §10 (`ADR-0055..0057`)
2. ICD §4 port table
3. Active MVP Contract rows cited in the packet
4. `slice/slice-findings.md`
5. VG-03 §6 (episode; run-termination vocabulary)
6. This index and the assigned packet
