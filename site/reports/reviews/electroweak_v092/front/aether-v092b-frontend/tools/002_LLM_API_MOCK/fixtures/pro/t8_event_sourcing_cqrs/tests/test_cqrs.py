import unittest
from cqrs import BankAccountAggregate, Event

class TestEventSourcing(unittest.TestCase):
    def test_aggregate_rehydration(self):
        events = [
            Event("AccountCreated", {"initial_balance": 100.0}, 1),
            Event("MoneyDeposited", {"amount": 50.0}, 2),
            Event("MoneyWithdrawn", {"amount": 30.0}, 3)
        ]
        acc = BankAccountAggregate("acc-123")
        for e in events:
            acc.apply(e)
        self.assertEqual(acc.balance, 120.0)
        self.assertEqual(acc.version, 3)

if __name__ == "__main__":
    unittest.main()
