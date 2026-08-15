"""Independent JSON Schema conformance checks for domain-generated examples."""
import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[4]
SCHEMAS = ROOT / "schemas" / "v4"
DOMAIN_SCHEMAS = Path(__file__).resolve().parents[1] / "schemas"


def validate(schema_path: Path, instance: dict) -> None:
    schema = json.loads(schema_path.read_text())
    store = {}
    for candidate in [*SCHEMAS.glob("*.schema.json"), *DOMAIN_SCHEMAS.glob("*.schema.json")]:
        loaded = json.loads(candidate.read_text())
        store[candidate.as_uri()] = loaded
        if "$id" in loaded:
            store[loaded["$id"]] = loaded
    resolver = RefResolver(schema_path.as_uri(), schema, store=store)
    Draft202012Validator(schema, resolver=resolver).validate(instance)


def test_existing_vectors() -> None:
    digest = lambda c: "sha256:" + c * 64
    validate(SCHEMAS / "effect-descriptor.schema.json", {
        "name": "fs.read", "args": {"target": "/workspace/README.md"}, "digest": digest("1")
    })
    validate(SCHEMAS / "capability-grant.schema.json", {
        "id": "grant-1", "principal": "agent-1", "descriptorDigest": digest("1"),
        "actions": ["fs.read"],
        "resources": [{"kind": "fs", "root": "file:///workspace", "paths": ["README.md"]}],
        "constraints": {"expiresAt": "2026-08-15T12:00:00.000Z", "maxUses": "1", "budgetLeaseId": "lease-1"},
        "purposeDigest": digest("2"),
    })
    validate(SCHEMAS / "event-envelope.schema.json", json.loads((SCHEMAS / "vectors/event-envelope/valid/evolution-scope.json").read_text()))
    validate(SCHEMAS / "evidence-claim.schema.json", json.loads((SCHEMAS / "vectors/evidence-claim/valid/minimal.json").read_text()))


def test_candidate_schemas() -> None:
    digest = lambda c: "sha256:" + c * 64
    validate(DOMAIN_SCHEMAS / "receipt.schema.json", {
        "descriptorDigest": digest("1"), "outcome": "ok",
        "observedAt": "2026-08-15T12:00:00.000Z", "resultDigest": digest("2"),
        "affectedResources": [{"resource": "file:///workspace/new", "change": "created", "postDigest": digest("3")}],
    })
    validate(DOMAIN_SCHEMAS / "artifact.schema.json", {
        "id": "artifact-1", "kind": "M", "artifactVersion": "1.0.0", "body": digest("1"),
        "interfaceSchema": "schema://method", "createdBy": "agent-1", "createdFrom": [],
        "dependencies": [], "supersedes": [], "contentDigest": digest("2"),
        "createdAt": "2026-08-15T12:00:00.000Z",
        "invalidationConditions": [{"condition": "suite fails", "checkKind": "automatic", "checkRef": "eval-suite"}],
    })


if __name__ == "__main__":
    test_existing_vectors()
    test_candidate_schemas()
    print("schema conformance: ok")
