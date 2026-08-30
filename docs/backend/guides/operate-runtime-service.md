---
id: guide.operate-service
canonical_id: guide.operate-service
class: how-to
authority: descriptive
truth_plane: AS_BUILT
status: living
implementation_status: IMPLEMENTED
owner: guides-operator
canonical_for:
  - daemon operation procedure
  - socket/config checks
  - stream/reconnect/approval procedure
purpose: Operational guide for starting the runtime service daemon, managing socket IPC, streaming events, resolving approvals, and bridging to Studio.
audience:
  - operator
  - developer
analysis_subject_sha: 9fd444674bf3a97f2673ff36a5f5928ef046c574
version: 0.9.1a1
last_verified: 2026-08-29
evidence:
  - E-B-005
  - E-B-044
  - E-B-045
  - E-B-046
  - E-B-048
  - E-B-049
  - E-B-052
relationships:
  - arch.interfaces.clients
  - ref.runtime-service
  - ref.commands
reviewer: documentation-specialist
confidence: high
---

# Operate Runtime Service Daemon Guide

## Purpose
This guide is the canonical owner for operational procedures governing the `vanguard-daemon` background process, UNIX domain socket lifecycle, event streaming, operator approval workflows, and Vanguard Studio gateway operations.

## Scope
- Starting, monitoring, and stopping `vanguard-daemon`.
- Submitting runs via `vg run` and `StartRun` commands.
- Live event streaming and connection recovery (`StreamEvents`).
- Submitting Ed25519-signed operator approvals (`ResolveApproval`).
- Launching the Vanguard Studio visual gateway.
- Handling the known `StartRun` profile default caveat (`UNR-B-001`).

## Non-responsibilities
- Exact JSON Schema specifications for `vg.4` frames (owned by [`ref.runtime-service`](../reference/runtime-service.md)).
- Core runtime execution architecture (owned by [`arch.runtime.execution`](../architecture/runtime-execution.md)).

## AS_BUILT Status
- `IMPLEMENTED` — Daemon server, IPC socket handling, and client streaming are operational in `vanguard.packages.runtime.service`.

---

## 1. Starting the Daemon

Launch the runtime daemon service:

```bash
# Start in background or active terminal
vanguard-daemon --socket /tmp/vanguard.sock
```

Or start the daemon via the TypeScript CLI:

```bash
vg daemon start
```

### Verification
Check socket reachability:
```bash
vg doctor
```

---

## 2. Submitting a Run via TypeScript CLI (`vg`)

Submit a task command to the running daemon:

```bash
# IMPORTANT: Explicitly specify --profile product to avoid UNR-B-001 default defect
vg run "Analyze repository dependencies" --profile product
```

---

## 3. Streaming Events & Reconnecting

Subscribe to real-time events from an active run:

```bash
vg trace --run-id 018f3a9a-7c20-7000-8000-000000000001
```

If the connection drops, `client-core` automatically reconnects and re-issues `StreamEvents` with `afterSeq` set to the last received sequence number.

---

## 4. Operator Approvals & Interventions

When a tool or effect requires human authorization (e.g. file deletion or network access under `approval_default: "ask"`):

1. The run pauses in `ESCALATED` state; `AuthorizationRequested` is emitted.
2. The operator inspects the pending request details:
   ```bash
   vg why --run-id 018f3a9a-7c20-7000-8000-000000000001
   ```
3. The operator signs and submits approval:
   ```bash
   vg approve --run-id 018f3a9a-7c20-7000-8000-000000000001 --request-id 018f... --decision allow
   ```

---

## 5. Launching Vanguard Studio Gateway

To view real-time execution graphs and artifacts in a web browser:

```bash
vanguard-studio --port 8080 --socket /tmp/vanguard.sock
```

Open `http://localhost:8080` in a browser.

---

## 6. Known Profile Default Defect & Workaround (`UNR-B-001`)

- **Caveat**: The TypeScript `vg` CLI client does not transmit `profileId` if omitted, causing the daemon to fall back to `code-default` in legacy paths, which is unsupported.
- **Workaround**: Always include `--profile product` or `--profile local` when launching runs via `vg run`.

---

## Related Documentation
- [Runtime Service Protocol Reference (`vg.4`)](../reference/runtime-service.md)
- [Application Interfaces Architecture](../architecture/application-interfaces.md)
- [Commands Reference](../reference/commands.md)
