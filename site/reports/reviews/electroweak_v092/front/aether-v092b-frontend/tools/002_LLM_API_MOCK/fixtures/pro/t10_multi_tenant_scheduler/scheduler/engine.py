from typing import Dict, List, Optional
from .tenant import TenantProfile, QuotaExceededError
from .queue import Task, TaskQueue

class DRFScheduler:
    def __init__(self, total_cpu: float, total_mem: float):
        self.total_cpu = total_cpu
        self.total_mem = total_mem
        self.tenants: Dict[str, TenantProfile] = {}
        self.queue = TaskQueue()
        self.scheduled_history: List[str] = []

    def register_tenant(self, profile: TenantProfile) -> None:
        self.tenants[profile.tenant_id] = profile

    def submit_task(self, task: Task) -> None:
        if task.tenant_id not in self.tenants:
            raise ValueError(f"unknown tenant {task.tenant_id}")
        tenant = self.tenants[task.tenant_id]
        if tenant.burst_credits <= 0:
            raise QuotaExceededError(f"tenant {task.tenant_id} exhausted burst credits")
        tenant.burst_credits -= 1
        self.queue.push(task)

    def schedule_next(self) -> Optional[Task]:
        # BENCHMARK SKELETON: Selects tenant with lowest dominant share
        candidate_tenants = [t for t in self.tenants.values() if self.queue.has_tasks_for(t.tenant_id)]
        if not candidate_tenants:
            return None
        candidate_tenants.sort(key=lambda t: t.dominant_share(self.total_cpu, self.total_mem))
        chosen_tenant = candidate_tenants[0]
        task = self.queue.pop_for_tenant(chosen_tenant.tenant_id)
        if task:
            chosen_tenant.allocated_cpu += task.cpu_cost
            chosen_tenant.allocated_mem += task.mem_cost
            self.scheduled_history.append(task.task_id)
        return task
