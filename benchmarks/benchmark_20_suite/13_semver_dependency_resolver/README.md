# Greenfield PRD: SemVer Dependency Resolver

## Objective
Implement `SemverResolver` and `ConflictError` in `src/resolver.py`.

## Requirements
- `SemverResolver()`
- `add_package(name: str, version: str, dependencies: dict[str, str] | None = None) -> None`: Registers package version with constraints (e.g. `{"depA": "^1.0.0"}`).
- `resolve(root_name: str, root_constraint: str) -> dict[str, str]`: Resolves package dependency tree, returning a dictionary `{pkg_name: selected_version}`.
- Constraints support exact (`1.0.0`), caret (`^1.2.0` matches `>=1.2.0, <2.0.0`), and range (`>=1.0.0, <2.0.0`).
- Raises `ConflictError` when no valid version combination satisfies all requirements.
