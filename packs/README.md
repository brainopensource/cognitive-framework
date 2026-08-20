# packs/

Domain packs. The kernel stays domain-blind (`coding|ast|pytest` must not land in `layer0/` or `vanguard/packages/{domain,kernel}/`).

**On disk:** `code-default/` — first MHF-shaped coding harness (`harness.yaml`, plugin yaml, fs / ast-patch / repo-map / terminal). Tests: `test/packs/`.

**Planned:** Wave 3–4 extract remaining coding leftovers from `vanguard/packages/runtime/` into packs; Wave 4 is one real coding-agent E2E on this pack + `vg`. Extra packs after that.

Older as-built harness configs still live under `vanguard/packages/agency/manifests/vg-*`.

See [`../README.md`](../README.md) and [`../docs/SPEC.md`](../docs/SPEC.md) §4.
