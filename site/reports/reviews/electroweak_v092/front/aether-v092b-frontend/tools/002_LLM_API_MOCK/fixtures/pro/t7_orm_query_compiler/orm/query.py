from typing import Dict, List, Any, Optional

class JoinCycleError(Exception):
    pass

class QuerySet:
    def __init__(self, model: type):
        self.model = model
        self.filters: List[tuple] = []
        self.selected_relations: List[str] = []
        self.limit_val: Optional[int] = None
        self.offset_val: Optional[int] = None

    def filter(self, **kwargs) -> "QuerySet":
        qs = self._clone()
        for k, v in kwargs.items():
            qs.filters.append((k, v))
        return qs

    def select_related(self, *fields: str) -> "QuerySet":
        qs = self._clone()
        qs.selected_relations.extend(fields)
        return qs

    def limit(self, count: int) -> "QuerySet":
        qs = self._clone()
        qs.limit_val = count
        return qs

    def offset(self, count: int) -> "QuerySet":
        qs = self._clone()
        qs.offset_val = count
        return qs

    def _clone(self) -> "QuerySet":
        qs = QuerySet(self.model)
        qs.filters = list(self.filters)
        qs.selected_relations = list(self.selected_relations)
        qs.limit_val = self.limit_val
        qs.offset_val = self.offset_val
        return qs
