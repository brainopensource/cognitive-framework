"""Registry managing registered deterministic artifact transforms."""

from __future__ import annotations

from typing import Iterable, Mapping

from ..domain.transforms.contracts import ArtifactTransform


class TransformRegistry:
    """In-memory registry of available artifact transformations."""

    def __init__(self, transforms: Iterable[ArtifactTransform] = ()) -> None:
        self._transforms: dict[str, ArtifactTransform] = {}
        for transform in transforms:
            self.register(transform)

    def register(self, transform: ArtifactTransform) -> None:
        """Register an artifact transform under its declared transform_id."""
        spec = transform.spec
        self._transforms[spec.transform_id] = transform

    def get(self, transform_id: str) -> ArtifactTransform | None:
        """Look up a transform by its identifier."""
        return self._transforms.get(transform_id)

    def has(self, transform_id: str) -> bool:
        """Return True if a transform is registered for transform_id."""
        return transform_id in self._transforms

    def list_transforms(self) -> tuple[str, ...]:
        """Return sorted tuple of registered transform identifiers."""
        return tuple(sorted(self._transforms.keys()))
