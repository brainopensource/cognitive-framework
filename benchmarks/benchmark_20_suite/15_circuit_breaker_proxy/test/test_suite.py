import unittest
import time
from src.circuit_breaker import CircuitBreaker, CircuitState, CircuitBreakerOpenException

class TestCircuitBreaker(unittest.TestCase):
    def test_circuit_trips_and_recovers(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1, half_open_success_threshold=1)
        
        def failing_call():
            raise ValueError("service error")

        # 2 failures trip to OPEN
        for _ in range(2):
            with self.assertRaises(ValueError):
                cb.call(failing_call)

        self.assertEqual(cb.state, CircuitState.OPEN)

        # Fast failure while OPEN
        with self.assertRaises(CircuitBreakerOpenException):
            cb.call(lambda: "success")

        time.sleep(0.15)
        # Recovers to HALF_OPEN -> CLOSED on successful trial
        res = cb.call(lambda: "success")
        self.assertEqual(res, "success")
        self.assertEqual(cb.state, CircuitState.CLOSED)

if __name__ == "__main__":
    unittest.main()
