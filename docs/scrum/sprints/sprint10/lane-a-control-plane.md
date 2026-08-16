# Sprint 10 · Lane A — Control Plane

**Owner:** Senior A · **Backlog:** `011 §7` · **Refinement:** PLANNED, NOT REFINED

## S10-A-01 — Domain de-capture · **do this before TableWorld**

`adapters/models/invocation.py` currently holds the coding domain:

```python
KNOWN_TOOLS = {...}                                    # fs.read, fs.search, patch.apply, proc.exec
if action in {"fs.read","fs.write","patch.apply"}: ... # requires 'path'
if action == "fs.search": ...                          # requires 'pattern'
def _bind_resource(...): return {"kind":"fs","root":root,"path":...}
```

The manifest already carries everything needed: each tool schema has `name`, `verb` and a JSON
Schema for `args`; each capability row has `verb`, `sink`, `selector`, `risk`.

- [ ] Failing test: a manifest declaring a non-filesystem verb (`table.read`) with its own
      `args_schema` and `selector_binding` composes and translates — currently impossible
- [ ] Make the translator **generic**: tool call → alias → verb → validate `args` against the
      declared schema → bind the selector by the declared template
- [ ] `invocation.py` holds **zero** domain knowledge
- [ ] Unknown alias fails at **composition** (not turn 3)
- [ ] Commit

**DoD:** `grep -c "fs\.\|patch\.\|proc\." adapters/models/invocation.py` → **0**

## S10-A-02 — `proc.test` orphan

Present in `KNOWN_TOOLS`, absent from `DEFAULT_BINDINGS`; the default pack's test tool is already
`verb: proc.exec`.

- [ ] Prefer deleting the orphan and keeping tests as allowlisted `proc.exec` (`D-04` guidance)
- [ ] Test: no verb in the translator lacks a binding
- [ ] Commit

## S10-A-03 — `BlobStorePort` + `IndexPort`

- [ ] Two implementations each (fake + real) per `T10.2`
- [ ] These are the seams every future memory/retrieval feature needs; their absence is why `O-02`
      has nowhere to land
- [ ] Commit

## S10-A-04 — `vg why <artifact>`

- [ ] What evidence activated it · what it predicts · what would demote it
- [ ] Reads from the ledger and the `Claim` store (`S8-A-05`)
- [ ] Commit

> `T6.5`: *"If the operator cannot interrogate governance, they will bypass it."* This is also the
> product differentiator — a harness that ships with its own evidence ledger.
