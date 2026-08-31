# Specification: TCB Monetary Budget Exact Conservation (TCB-05)

Monetary budgets in the TCB must be calculated using integer micro-units (`usd_micros` where 1 USD = 1,000,000 micros) or exact `Decimal` representation:
1. Float arithmetic drift MUST NOT occur during reserve and refund operations.
2. `remaining_balance()` must return exact results without precision loss.
