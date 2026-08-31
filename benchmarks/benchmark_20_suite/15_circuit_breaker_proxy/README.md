# Greenfield PRD: Resilient Circuit Breaker Middleware

## Objective
Implement `CircuitBreaker`, `CircuitState`, and `CircuitBreakerOpenException` in `src/circuit_breaker.py`.

## Requirements
- `CircuitState` enum: `CLOSED`, `OPEN`, `HALF_OPEN`.
- `CircuitBreaker(failure_threshold: int = 3, recovery_timeout: float = 0.5, half_open_success_threshold: int = 2)`
- `call(func: Callable, *args, **kwargs) -> Any`: Executes `func`.
  - When `CLOSED`: Failure increments count. Reaching `failure_threshold` trips state to `OPEN`.
  - When `OPEN`: Raises `CircuitBreakerOpenException` immediately without calling `func`. If `recovery_timeout` has elapsed, transitions to `HALF_OPEN`.
  - When `HALF_OPEN`: Allows trial calls. If `half_open_success_threshold` consecutive calls succeed, transitions to `CLOSED`. Any failure reverts to `OPEN`.
- `state` property returning current `CircuitState`.
