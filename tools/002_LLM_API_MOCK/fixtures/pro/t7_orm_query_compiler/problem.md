# Problem: ORM Query Compiler & Join Graph Resolution (Tier 7)

Implement an ANSI SQL AST Query Compiler that compiles fluent `QuerySet` expressions into parameterized SQL queries with automatic table aliasing, cyclic join prevention, and filter pushdown.

### Requirements:
1. `QuerySet.filter(**kwargs)` must support exact matches, `__in`, `__gt`, `__lt`, and nested relation traversal (e.g. `author__organization__country="US"`).
2. `QuerySet.select_related(*fields)` must generate `INNER JOIN` or `LEFT OUTER JOIN` clauses with distinct deterministic aliases (`t0`, `t1`, etc.).
3. Joining the same relation twice through multiple filters must reuse existing join table aliases without generating redundant duplicate joins.
4. Circular foreign key traversals must raise `JoinCycleError` instead of infinite recursion.
5. `Compiler.compile(queryset)` returns `(sql: str, params: list)`.
