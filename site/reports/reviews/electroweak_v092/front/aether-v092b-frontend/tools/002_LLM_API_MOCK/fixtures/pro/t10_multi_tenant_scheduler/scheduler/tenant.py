from dataclasses import dataclass

class QuotaExceededError(Exception):
    pass

@dataclass
class TenantProfile:
    tenant_id: str
    cpu_limit: float
    mem_limit: float
    burst_credits: int = 10
    allocated_cpu: float = 0.0
    allocated_mem: float = 0.0

    def dominant_share(self, total_cpu: float, total_mem: float) -> float:
        s_cpu = self.allocated_cpu / max(1.0, total_cpu)
        s_mem = self.allocated_mem / max(1.0, total_mem)
        return max(s_cpu, s_mem)
