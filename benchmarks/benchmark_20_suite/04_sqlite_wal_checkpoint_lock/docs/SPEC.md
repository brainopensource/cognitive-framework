# Specification: SQLite WAL Concurrency & Lock Resilience (STO-04)

The `SqliteEventStore` MUST:
1. Enable `timeout=30.0` on connection creation.
2. Execute `PRAGMA busy_timeout = 30000;` during initialization.
3. Handle concurrent writes and checkpoints gracefully without raising `sqlite3.OperationalError: database is locked`.
