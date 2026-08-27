from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Event:
    event_type: str
    data: Dict[str, Any]
    version: int

class BankAccountAggregate:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance: float = 0.0
        self.version: int = 0

    def apply(self, event: Event) -> None:
        if event.event_type == "AccountCreated":
            self.balance = event.data.get("initial_balance", 0.0)
        elif event.event_type == "MoneyDeposited":
            self.balance += event.data.get("amount", 0.0)
        elif event.event_type == "MoneyWithdrawn":
            self.balance -= event.data.get("amount", 0.0)
        self.version = event.version
