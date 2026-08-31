# Specification: Monotonic Capability Attenuation (TCB-03)

In accordance with the Principle of Least Privilege and Invariant I-5:
1. When a child agent is spawned, its effective scopes for any capability MUST be the strict intersection:
   `effective_scopes = parent_cap.scopes & requested_cap.scopes`
2. A child agent MUST NEVER acquire permissions or scopes absent from the parent's capability set.
