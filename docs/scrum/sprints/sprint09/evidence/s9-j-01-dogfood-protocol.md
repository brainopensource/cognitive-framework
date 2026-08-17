# Dogfood Protocol — S9-J-01 (Pre-Registered Bug Specifications)

**Status:** Pre-registered  
**Target:** Live interactive dogfooding (not LAM replay / cassette runs)

Three bug instances pre-registered before human trial execution:

1. **`DOGFOOD-01: multi-turn-file-rollback`**
   - **Fault:** Agent applies a malformed patch, receives compiler syntax error receipt, but fails to rollback or re-read before issuing another diff, causing corrupt hunk application.
   - **Target Behaviour:** Agent must observe syntax receipt, restore snapshot or issue clean replacement, and compile green.

2. **`DOGFOOD-02: subprocess-timeout-censoring`**
   - **Fault:** Subprocess execution running long test suite hangs and fails silently instead of reporting right-censored timeout.
   - **Target Behaviour:** `proc.exec` produces deterministic `timeout` status receipt within lease bounds.

3. **`DOGFOOD-03: manifest-alias-shadowing`**
   - **Fault:** Custom alias inadvertently maps to ungranted kernel verb.
   - **Target Behaviour:** Composition refuses fail-closed with `UnresolvableVerbError`.
