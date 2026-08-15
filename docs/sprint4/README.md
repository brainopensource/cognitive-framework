# Sprint 4 developer packet index

Project decision: `NOT STARTED — after Sprint 3 integration`  
Decisions: `ADR-0047`, `ADR-0048`, `ADR-0055`, `ADR-0056`

Split a/b. Same four people. OpenRouter is parallel and **off** the trust-spine command.

| Half | Lane | Packet | Cx | Contract |
|---|---|---|---|---|
| S4a | Senior A | `sa-packet.md` | 5 GATE | `REQ-TRUST-001` (trajectory; deletion is S4b) |
| S4a | Developer C | `dc-packet.md` | 3 GATE | `REQ-PORT-006` |
| S4b | Senior B | `sb-packet.md` | 4 GATE | `REQ-SEC-001` |
| S4b | Developer D | `dd-packet.md` | 2 FAST | `REQ-PORT-003` real Git |
| S4 exit | Senior A + Sr B | `S4-GATE-001` | 5 | `REQ-TRUST-001` + `MF-S4-001` |

S5 (evaluator OS identity, context compiler) and S6 (wire OpenRouter + Git into `vg run`, dogfood) are not this sprint.
