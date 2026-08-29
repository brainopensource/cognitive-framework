"""Runtime execution wrapper for pure, deterministic artifact transforms."""

from __future__ import annotations

from typing import Any, Mapping

from ..domain.transforms.contracts import (
    ArtifactTransform,
    TransformDiagnostic,
    TransformOutput,
    TransformResult,
)
from ..ports.blob_store import BlobStorePort
from .transform_registry import TransformRegistry


class TransformRuntime:
    """Executes pure artifact transforms against a content-addressed blob store."""

    def __init__(
        self,
        blob_store: BlobStorePort,
        registry: TransformRegistry | None = None,
    ) -> None:
        self._blob_store = blob_store
        self._registry = registry if registry is not None else TransformRegistry()

    @property
    def registry(self) -> TransformRegistry:
        return self._registry

    def execute(
        self,
        transform_id: str,
        input_digest: str,
        config: Mapping[str, Any] | None = None,
    ) -> TransformResult:
        """Fetch input artifact, enforce resource bounds, invoke transform, and persist output."""
        transform = self._registry.get(transform_id)
        if transform is None:
            return TransformResult(
                status="fatal_error",
                output_digest=None,
                output_schema=None,
                diagnostics=(
                    TransformDiagnostic(
                        code="TRANSFORM_NOT_FOUND",
                        severity="error",
                        message=f"Transform '{transform_id}' is not registered",
                    ),
                ),
                confidence_ppm=0,
            )

        spec = transform.spec

        # 1. Retrieve input bytes
        get_res = self._blob_store.get(input_digest)
        if not get_res.ok or get_res.value is None:
            return TransformResult(
                status="fatal_error",
                output_digest=None,
                output_schema=None,
                diagnostics=(
                    TransformDiagnostic(
                        code="INPUT_NOT_FOUND",
                        severity="error",
                        message=f"Input artifact '{input_digest}' could not be retrieved",
                    ),
                ),
                confidence_ppm=0,
            )

        payload = get_res.value

        # 2. Check input bounds
        if len(payload) > spec.max_input_bytes:
            return TransformResult(
                status="rejected",
                output_digest=None,
                output_schema=None,
                diagnostics=(
                    TransformDiagnostic(
                        code="INPUT_TOO_LARGE",
                        severity="error",
                        message=f"Input payload ({len(payload)} bytes) exceeds limit ({spec.max_input_bytes} bytes)",
                    ),
                ),
                confidence_ppm=0,
            )

        # 3. Apply pure transform
        try:
            output: TransformOutput = transform.apply(payload, config)
        except Exception as exc:
            return TransformResult(
                status="fatal_error",
                output_digest=None,
                output_schema=None,
                diagnostics=(
                    TransformDiagnostic(
                        code="TRANSFORM_EXCEPTION",
                        severity="error",
                        message=f"Transform raised unexpected error: {exc}",
                    ),
                ),
                confidence_ppm=0,
            )

        # 4. Check output payload and persist
        output_digest = None
        if output.payload is not None:
            if len(output.payload) > spec.max_output_bytes:
                return TransformResult(
                    status="rejected",
                    output_digest=None,
                    output_schema=None,
                    diagnostics=(
                        TransformDiagnostic(
                            code="OUTPUT_TOO_LARGE",
                            severity="error",
                            message=f"Output payload ({len(output.payload)} bytes) exceeds limit ({spec.max_output_bytes} bytes)",
                        ),
                    ),
                    confidence_ppm=0,
                )
            put_res = self._blob_store.put(output.payload)
            if not put_res.ok or put_res.value is None:
                return TransformResult(
                    status="fatal_error",
                    output_digest=None,
                    output_schema=None,
                    diagnostics=(
                        TransformDiagnostic(
                            code="BLOB_STORE_ERROR",
                            severity="error",
                            message="Failed to persist transform output artifact",
                        ),
                    ),
                    confidence_ppm=0,
                )
            output_digest = put_res.value

        return TransformResult(
            status=output.status,
            output_digest=output_digest,
            output_schema=output.output_schema or spec.output_schema,
            diagnostics=output.diagnostics,
            confidence_ppm=output.confidence_ppm,
        )
