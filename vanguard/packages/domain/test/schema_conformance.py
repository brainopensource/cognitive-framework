"""Independent jsonschema replay of every active T1 valid vector."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "schemas" / "v4"

CONTRACTS = {
    "effect-descriptor": "effect-descriptor.schema.json",
    "capability-grant": "capability-grant.schema.json",
    "receipt": "receipt.schema.json",
    "event-envelope": "event-envelope.schema.json",
    "artifact": "artifact.schema.json",
    "evidence-claim": "evidence-claim.schema.json",
    "correction-record": "correction-record.schema.json",
    "recording": "recording.schema.json",
    "process-definition": "process-definition.schema.json",
    "process-instance": "process-instance.schema.json",
}


def validate(schema_path: Path, instance: object) -> None:
    schema = json.loads(schema_path.read_text())
    store = {}
    for candidate in SCHEMAS.glob("*.schema.json"):
        loaded = json.loads(candidate.read_text())
        store[candidate.as_uri()] = loaded
        if "$id" in loaded:
            store[loaded["$id"]] = loaded
    resolver = RefResolver(schema_path.as_uri(), schema, store=store)
    Draft202012Validator(schema, resolver=resolver).validate(instance)


def test_active_vectors() -> None:
    for vector_dir, schema_name in CONTRACTS.items():
        paths = sorted((SCHEMAS / "vectors" / vector_dir / "valid").glob("*.json"))
        if not paths:
            raise AssertionError(f"{vector_dir} has no valid vector")
        for path in paths:
            validate(SCHEMAS / schema_name, json.loads(path.read_text()))


if __name__ == "__main__":
    test_active_vectors()
    print("schema conformance: ok")
