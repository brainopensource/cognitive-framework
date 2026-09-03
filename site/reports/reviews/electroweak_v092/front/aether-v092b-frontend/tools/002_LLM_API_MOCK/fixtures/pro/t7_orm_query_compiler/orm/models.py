from typing import Dict, Any, Optional

class Field:
    def __init__(self, primary_key: bool = False):
        self.primary_key = primary_key
        self.name: str = ""

class ForeignKey:
    def __init__(self, to: type, related_name: Optional[str] = None):
        self.to = to
        self.related_name = related_name
        self.name: str = ""

class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        fields = {}
        for k, v in list(attrs.items()):
            if isinstance(v, (Field, ForeignKey)):
                v.name = k
                fields[k] = v
        attrs["_fields"] = fields
        attrs["_table"] = name.lower() + "s"
        return super().__new__(mcs, name, bases, attrs)

class Model(metaclass=ModelMeta):
    _fields: Dict[str, Any] = {}
    _table: str = ""
