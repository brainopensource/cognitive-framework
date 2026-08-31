# Greenfield PRD: In-Memory Event Bus with Wildcard Routing and DLQ

## Objective
Implement `EventBus` and `DeadLetterItem` in `src/event_bus.py`.

## Requirements
- `EventBus()`
- `subscribe(pattern: str, handler: Callable[[str, Any], None]) -> str`: Returns subscription ID.
  - Supports exact matching (`"order.created"`).
  - Supports single-word wildcard `*` (`"order.*"` matches `"order.created"`, `"order.cancelled"`).
  - Supports multi-word wildcard `#` (`"order.#"` matches `"order.us.created"`).
- `unsubscribe(sub_id: str) -> bool`
- `publish(topic: str, data: Any) -> int`: Dispatches to all matching handlers. If a handler raises an exception, the error and event are captured into Dead-Letter Queue (DLQ) without breaking other handlers. Returns count of successful dispatches.
- `get_dlq() -> list[DeadLetterItem]`
