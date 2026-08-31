# Specification: Rate Limiter Token Conservation (Invariant K-09)

The `RateLimiter` must maintain the invariant:
`self.available + sum(lease['tokens'] for lease in self.active_leases.values()) == self.capacity`

When `clean_expired(current_time)` is invoked:
1. All leases where `expires_at <= current_time` MUST be removed from `active_leases`.
2. The tokens allocated to each expired lease MUST be returned to `self.available`.
3. The method must return the integer count of cleaned leases.
