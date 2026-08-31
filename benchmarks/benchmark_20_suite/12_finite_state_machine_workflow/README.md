# Greenfield PRD: Deterministic Finite State Machine (FSM)

## Objective
Implement `StateMachine` and `InvalidTransitionError` in `src/fsm.py`.

## Requirements
- `StateMachine(initial_state: str)`
- `add_transition(source: str, event: str, target: str, guard: Callable[..., bool] | None = None)`
- `trigger(event: str, **kwargs) -> str`: Transitions state. Raises `InvalidTransitionError` if no transition matches or guard returns `False`. Returns new state.
- `current_state: str` property.
- `history: list[dict]` property: Returns history of transitions `[{"from": ..., "event": ..., "to": ...}]`.
