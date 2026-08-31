# Greenfield PRD: Hierarchical Token Bucket Rate Limiter

## Objective
Implement `HierarchicalTokenBucket` in `src/token_bucket.py`.

## Requirements
- `HierarchicalTokenBucket(capacity: float, refill_rate: float, parent: Optional[HierarchicalTokenBucket] = None)`
- `acquire(tokens: float) -> bool`: Consumes tokens from this bucket AND all ancestor parent buckets. If any bucket in the hierarchy lacks sufficient tokens, no tokens are consumed from any bucket (atomic) and returns `False`.
- Refills tokens continuously based on `refill_rate` (tokens per second) up to `capacity`.
- Thread-safe.
