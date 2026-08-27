# Problem: Multi-Tenant Kernel Scheduler & Dominant Resource Fairness (Tier 10)

Implement an asynchronous fair-share task scheduler enforcing Dominant Resource Fairness (DRF) across heterogeneous compute vectors (CPU, Memory, IO bandwidth) with starvation prevention and token burst limits.

### Requirements:
1. `TenantProfile`: defined with `(cpu_weight, mem_weight, max_burst_credits)`.
2. Dominant share calculation:
   $$\text{dominant\_share}(T) = \max\left(\frac{\text{alloc\_cpu}}{\text{total\_cpu}}, \frac{\text{alloc\_mem}}{\text{total\_mem}}\right)$$
3. Scheduling policy: Pick next runnable task from tenant with the MINIMUM dominant share.
4. Preemptive starvation prevention: Tenants starved for $> \tau$ time units must receive priority boost.
5. Throttling: Reject submissions when a tenant exceeds burst quota.
