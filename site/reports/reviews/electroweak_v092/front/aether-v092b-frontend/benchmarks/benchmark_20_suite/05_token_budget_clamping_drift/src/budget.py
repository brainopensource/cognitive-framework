from typing import Optional

class BudgetGovernor:
    def __init__(self, initial_usd: float = 10.0):
        # BUG: Storing and computing balance in native float causes arithmetic
        # precision drift over repeated micro-transactions (e.g. 0.0001 reserve/refund).
        self.initial_usd = initial_usd
        self.available_usd = initial_usd

    def reserve(self, amount_usd: float) -> bool:
        if amount_usd > self.available_usd:
            return False
        self.available_usd -= amount_usd
        return True

    def refund(self, amount_usd: float) -> None:
        self.available_usd += amount_usd

    def commit(self, amount_usd: float) -> None:
        pass

    def remaining_balance(self) -> float:
        return self.available_usd
