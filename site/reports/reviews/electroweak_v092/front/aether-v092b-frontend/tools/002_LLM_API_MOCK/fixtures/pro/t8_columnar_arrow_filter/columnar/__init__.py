from typing import List, Dict, Any, Callable

class ColumnChunk:
    def __init__(self, name: str, values: List[Any]):
        self.name = name
        self.values = values

    def filter_bitmap(self, predicate: Callable[[Any], bool]) -> List[int]:
        # Returns indices matching predicate
        return [i for i, v in enumerate(self.values) if predicate(v)]

class ColumnarTable:
    def __init__(self, columns: Dict[str, List[Any]]):
        self.columns = {k: ColumnChunk(k, v) for k, v in columns.items()}
        self.length = len(next(iter(columns.values()))) if columns else 0

    def query(self, col_name: str, predicate: Callable[[Any], bool]) -> Dict[str, List[Any]]:
        chunk = self.columns[col_name]
        matching_indices = set(chunk.filter_bitmap(predicate))
        return {
            k: [v for i, v in enumerate(c.values) if i in matching_indices]
            for k, c in self.columns.items()
        }
