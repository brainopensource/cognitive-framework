# Specification: Sandbox Evaluator Timeout Termination (EVL-08)

The `SandboxRunner` must:
1. Enforce process execution timeout strictly.
2. When a timeout occurs, return `ExecutionResult(status="TIMEOUT", return_code=-1, stdout=..., stderr=...)`.
