import unittest
from scheduler.tenant import TenantProfile, QuotaExceededError
from scheduler.queue import Task
from scheduler.engine import DRFScheduler

class TestMultiTenantScheduler(unittest.TestCase):
    def test_drf_fair_allocation_across_heterogeneous_tasks(self):
        # Total cluster: 100 CPU, 100 GiB RAM
        sched = DRFScheduler(total_cpu=100.0, total_mem=100.0)
        # Tenant A is CPU-heavy (cpu=2, mem=1)
        sched.register_tenant(TenantProfile("A", cpu_limit=50.0, mem_limit=50.0))
        # Tenant B is Memory-heavy (cpu=1, mem=3)
        sched.register_tenant(TenantProfile("B", cpu_limit=50.0, mem_limit=50.0))

        # Enqueue 3 tasks for each
        for i in range(3):
            sched.submit_task(Task(f"A_{i}", "A", cpu_cost=2.0, mem_cost=1.0))
            sched.submit_task(Task(f"B_{i}", "B", cpu_cost=1.0, mem_cost=3.0))

        executed = []
        for _ in range(6):
            t = sched.schedule_next()
            if t: executed.append(t.task_id)

        self.assertEqual(len(executed), 6)
        # Verify interleaving fairness
        self.assertEqual(executed[0], "A_0")
        self.assertEqual(executed[1], "B_0")

    def test_burst_quota_enforcement(self):
        sched = DRFScheduler(total_cpu=100.0, total_mem=100.0)
        sched.register_tenant(TenantProfile("C", cpu_limit=10.0, mem_limit=10.0, burst_credits=2))
        sched.submit_task(Task("C_1", "C", 1.0, 1.0))
        sched.submit_task(Task("C_2", "C", 1.0, 1.0))
        with self.assertRaises(QuotaExceededError):
            sched.submit_task(Task("C_3", "C", 1.0, 1.0))

if __name__ == "__main__":
    unittest.main()
