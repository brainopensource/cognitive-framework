from typing import Dict, List, Any

class SchemaStitcher:
    def __init__(self):
        self.subgraphs: Dict[str, Dict[str, List[str]]] = {}

    def register_subgraph(self, name: str, type_fields: Dict[str, List[str]]) -> None:
        self.subgraphs[name] = type_fields

    def resolve_query(self, type_name: str, requested_fields: List[str]) -> Dict[str, List[str]]:
        # Maps subgraph -> fields to fetch
        plan: Dict[str, List[str]] = {}
        for field in requested_fields:
            resolved = False
            for sg_name, types in self.subgraphs.items():
                if type_name in types and field in types[type_name]:
                    plan.setdefault(sg_name, []).append(field)
                    resolved = True
                    break
            if not resolved:
                raise ValueError(f"Unresolvable field {field} on type {type_name}")
        return plan
