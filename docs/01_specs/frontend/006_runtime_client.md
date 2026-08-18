# 006 — RuntimeClient implementer note (Proposed)

Status: `Proposed`  
Date: 2026-08-17  
Source: `@vanguard/client-core` (`src/contract/types.ts`, `parse.ts`, `adapters/live.ts`, `replay.ts`, `scenario.ts`, `signer.ts`).

## Port

`RuntimeClient` methods return `Promise<Result<T>>` except `streamEvents`, which is `AsyncIterable<Result<StreamItem>>`. Failures are `ClientFailure` codes; do not throw for expected daemon/transport errors.

`StreamItem` always includes `contractVersion: "0.1"`, `source`, and a parsed `envelope`.

## Live frames

See `003_wire_consumer.md`. Transports: `SocketTransport` (UDS) and `FeedTransport` (injected lines). Incoming lines are parsed (`parse.ts`); `frame: any` is forbidden (`CT-03`).

## Ring buffer

Live adapter retains at most **10_000** `StreamItem`s (`MAX_BUFFER_SIZE`). Drop oldest. Reducers must tolerate truncated history after reconnect (`afterSeq`).

## Keys (FE-1-2 / FE-A3)

Operator Ed25519 private key persists under `~/.vanguard/keys` with mode **0600**. Never log PEM. Signing input is RFC-8785 canonical JSON of the decision payload (003). Round-trip against Python `OperatorSigner` golden vectors.

## Honest holes

| Method | Until backend supports it |
|---|---|
| `getDaemonStatus` | Connect-only; do not hardcode a marketing version as proof of health |
| `explainArtifact` | `not_available` if daemon has no projection |
| `manageDaemon` / spawn | `not_available` until Joint **J1** |
