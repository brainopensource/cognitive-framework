from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Task:
    task_id: str
    tenant_id: str
    cpu_cost: float
    mem_cost: float

class TaskQueue:
    def __init__(self):
        self._tasks: List[Task] = []

    def push(self, task: Task) -> None:
        self._tasks.append(task)

    def pop_for_tenant(self, tenant_id: str) -> Optional[Task]:
        for i, t in enumerate(self._tasks):
            if t.tenant_id == tenant_id:
                return self._tasks.pop(i)
        return None

    def has_tasks_for(self, tenant_id: str) -> bool:
        return any(t.tenant_id == tenant_id for t in self._tasks)

    @property
    def total_pending(self) -> int:
        return len(self._tasks)
