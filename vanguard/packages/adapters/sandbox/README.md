# sandbox adapters

`FakeSandboxRunner` is visibly non-contained. `RootlessSandboxRunner` constructs
a Bubblewrap worker namespace and derives its containment report from mount,
egress, and denied-syscall probes run inside that namespace. It exposes only the
worker workspace and temporary storage as writable mounts; the evaluator bundle
is deliberately absent from the worker mount tree.

If the runtime or any probe cannot establish the claimed boundary, the report
is marked `unverified-rootless-perimeter`. The shared publication decision then
blocks the result. Local runtime limitations therefore degrade explicitly and
never become an inferred containment claim.
