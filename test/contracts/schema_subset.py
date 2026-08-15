"""A minimal JSON Schema 2020-12 validator for the vector suites.

`CT-01`: the schemas in `schemas/v4/` are normative and a validator in any
language is an implementation verified against them. That verification needs
the schema itself to be executable in the test process, and the repository has
no third-party dependency budget, so this covers exactly the keywords the v4
schemas use — `type`, `const`, `enum`, `pattern`, `minLength`, `maxLength`,
`minimum`, `maximum`, `required`, `properties`, `additionalProperties`,
`items`, `minItems`, `oneOf`, `$ref`, `$defs`.

It is deliberately small and deliberately not in `vanguard/packages/`: it is
test scaffolding for reading the normative artifact, not a product validator.
An unsupported keyword raises rather than passing silently.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SUPPORTED = {
    "$schema", "$id", "$comment", "$defs", "$ref", "title", "type", "const",
    "enum", "pattern", "minLength", "maxLength", "minimum", "maximum",
    "required", "properties", "additionalProperties", "items", "minItems",
    "oneOf",
}

_TYPES = {
    "string": str,
    "object": dict,
    "array": list,
    "boolean": bool,
    "null": type(None),
}


class SchemaViolation(Exception):
    """Instance rejected. `keyword` is what the vector's expect file names."""

    def __init__(self, keyword: str, path: str, message: str) -> None:
        super().__init__(f"{path or '/'}: {message} ({keyword})")
        self.keyword = keyword
        self.path = path


class SchemaSet:
    """The schemas of one directory, resolvable by relative file reference."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.documents: dict[str, Any] = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in directory.glob("*.schema.json")
        }

    def resolve(self, ref: str, document: str) -> tuple[Any, str]:
        file_part, _, pointer = ref.partition("#")
        target = file_part or document
        node = self.documents[target]
        for token in filter(None, pointer.split("/")):
            node = node[token.replace("~1", "/").replace("~0", "~")]
        return node, target

    def validate(self, instance: Any, document: str, schema: Any = None,
                 path: str = "") -> None:
        if schema is None:
            schema = self.documents[document]
        for keyword in schema:
            if keyword not in SUPPORTED:
                raise AssertionError(f"unsupported schema keyword {keyword!r} in {document}")

        if "$ref" in schema:
            target, target_document = self.resolve(schema["$ref"], document)
            self.validate(instance, target_document, target, path)

        if "type" in schema:
            expected = schema["type"]
            if expected == "integer":
                if isinstance(instance, bool) or not isinstance(instance, int):
                    raise SchemaViolation("type", path, f"expected integer, got {instance!r}")
            else:
                python_type = _TYPES[expected]
                if isinstance(instance, bool) != (python_type is bool) or not isinstance(
                        instance, python_type):
                    raise SchemaViolation("type", path, f"expected {expected}, got {instance!r}")

        if "const" in schema and instance != schema["const"]:
            raise SchemaViolation("const", path, f"expected {schema['const']!r}")
        if "enum" in schema and instance not in schema["enum"]:
            raise SchemaViolation("enum", path, f"{instance!r} is not one of {schema['enum']}")

        if isinstance(instance, str):
            if "pattern" in schema and not re.search(schema["pattern"], instance):
                raise SchemaViolation("pattern", path, f"{instance!r} fails {schema['pattern']}")
            if "minLength" in schema and len(instance) < schema["minLength"]:
                raise SchemaViolation("minLength", path, "too short")
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                raise SchemaViolation("maxLength", path, "too long")

        if isinstance(instance, (int, float)) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                raise SchemaViolation("minimum", path, f"{instance} below minimum")
            if "maximum" in schema and instance > schema["maximum"]:
                raise SchemaViolation("maximum", path, f"{instance} above maximum")

        if isinstance(instance, list):
            if "minItems" in schema and len(instance) < schema["minItems"]:
                raise SchemaViolation("minItems", path, "too few items")
            if "items" in schema:
                for index, item in enumerate(instance):
                    self.validate(item, document, schema["items"], f"{path}/{index}")

        if isinstance(instance, dict):
            for field in schema.get("required", []):
                if field not in instance:
                    raise SchemaViolation("required", path, f"missing {field!r}")
            properties = schema.get("properties", {})
            for field, value in instance.items():
                if field in properties:
                    self.validate(value, document, properties[field], f"{path}/{field}")
                elif schema.get("additionalProperties") is False:
                    raise SchemaViolation("additionalProperties", path, f"unknown field {field!r}")

        if "oneOf" in schema:
            matched = []
            for index, option in enumerate(schema["oneOf"]):
                try:
                    self.validate(instance, document, option, path)
                except SchemaViolation:
                    continue
                matched.append(index)
            if len(matched) != 1:
                raise SchemaViolation("oneOf", path, f"{len(matched)} branches matched")
