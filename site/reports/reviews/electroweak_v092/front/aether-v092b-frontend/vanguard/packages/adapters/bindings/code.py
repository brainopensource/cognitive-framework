"""Code domain namespaced binding provider.

Owning contract: ADR-0088 §1.7, GTS-13C §7.3.
Hexagonal boundary: Adapters package (imports only domain and ports).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from ...domain.canonicalisation.digest import digest_of
from ...ports.environment import EffectRequest as EnvironmentRequest
from ...ports.environment import ObservationRequest


@dataclass(frozen=True, slots=True)
class CodeAdapterOutcome:
    """Outcome value object for the code domain adapter boundary."""

    status: str
    occurrence: str
    cost: Mapping[str, int]
    result_digest: str = "sha256:" + "0" * 64
    detail: str = ""

    @property
    def actual_cost(self) -> Mapping[str, int]:
        """Name used by the kernel outcome projection at the runtime seam."""
        return self.cost


class CodeEffectAdapter:
    """Effect adapter bridging filesystem, patch, and process effects to EnvironmentPort."""

    def __init__(self, verb: str, environment: Any, call_type: str = "apply") -> None:
        self.name = verb
        self.verb = verb
        self._environment = environment
        self._call_type = call_type

    def healthy(self) -> bool:
        if self._environment is None:
            return False
        required_method = "observe" if self._call_type == "observe" else "apply"
        if not callable(getattr(self._environment, required_method, None)):
            return False
        if hasattr(self._environment, "profile"):
            try:
                profile = self._environment.profile()
            except Exception:
                return False
            return bool(getattr(profile, "ok", False))
        return True

    def execute(self, request: Any) -> CodeAdapterOutcome:
        if self._environment is None:
            return CodeAdapterOutcome(
                status="error",
                occurrence="not_occurred",
                cost={"usd_micros": 0},
                detail="environment is not available",
            )

        if self._call_type == "observe":
            action = self.verb.split(".")[-1]
            args = getattr(request, "args", {}) or {}
            if not isinstance(args, Mapping):
                return CodeAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="effect args must be an object",
                )
            obs_req = ObservationRequest(
                action=action,
                path=args.get("path"),
                pattern=args.get("pattern"),
                args=dict(args),
            )
            result = self._environment.observe(obs_req)
            occurred = "occurred"
        else:
            args = getattr(request, "args", {}) or {}
            if not isinstance(args, Mapping):
                return CodeAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="effect args must be an object",
                )
            has_diff = "diff" in args or "patch" in args
            diff = args.get("diff") if "diff" in args else args.get("patch")
            has_argv = "argv" in args or "command" in args
            argv = args.get("argv") if "argv" in args else args.get("command")
            if has_diff and has_argv:
                return CodeAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="effect args cannot contain both patch and command",
                )
            if has_diff and not isinstance(diff, str):
                return CodeAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="patch/diff must be a string",
                )
            if has_argv and (
                isinstance(argv, str)
                or not isinstance(argv, (list, tuple))
                or not argv
                or not all(isinstance(item, str) for item in argv)
            ):
                return CodeAdapterOutcome(
                    status="error",
                    occurrence="not_occurred",
                    cost={"usd_micros": 0},
                    detail="command must be a non-empty argv array of strings",
                )
            action = "patch" if has_diff else ("exec" if has_argv else "write")
            eff_req = EnvironmentRequest(
                verb=self.verb,
                action=action,
                args=dict(args),
                patch=diff,
                command=tuple(argv) if argv else None,
                idempotency_key=getattr(request, "idempotency_key", None),
            )
            result = self._environment.apply(eff_req)
            occurred = "occurred" if getattr(result, "ok", False) else "undeterminable"

        if not getattr(result, "ok", False):
            error = getattr(result, "error", None)
            kind = getattr(error, "kind", "instrument_error") if error is not None else "instrument_error"
            message = getattr(error, "message", str(error)) if error is not None else "effect failed"
            return CodeAdapterOutcome(
                status="denied" if kind == "denied" else "error",
                occurrence="not_occurred" if kind in {"denied", "invalid_request", "not_found"} else occurred,
                cost={"usd_micros": 0},
                detail=message,
            )

        value = getattr(result, "value", None)
        detail = ""
        if hasattr(value, "content") and value.content is not None:
            detail = str(value.content)
        elif hasattr(value, "matches") and value.matches:
            detail = json.dumps(value.matches)
        elif hasattr(value, "files") and value.files:
            detail = json.dumps(value.files)
        elif hasattr(value, "output") and value.output is not None:
            detail = str(value.output)

        receipt_outcome = getattr(value, "outcome", None)
        status = "ok"
        if isinstance(receipt_outcome, str) and receipt_outcome not in {"", "ok"}:
            status = "error"
        exit_code = getattr(value, "exit_code", None)
        if isinstance(exit_code, int) and not isinstance(exit_code, bool):
            detail = f"[exit {exit_code}] {detail}" if detail else f"[exit {exit_code}]"

        metadata = getattr(value, "metadata", {}) or {}
        digest = getattr(value, "result_digest", None)
        if not digest and isinstance(metadata, Mapping):
            digest = metadata.get("digest")
        if not digest:
            if is_dataclass(value):
                digest_value: Any = asdict(value)
                if isinstance(digest_value, dict):
                    digest_value.pop("observed_at", None)
            elif isinstance(value, Mapping):
                digest_value = dict(value)
            else:
                digest_value = {"detail": detail, "exit_code": exit_code}
            digest = digest_of({"verb": self.verb, "value": digest_value})

        return CodeAdapterOutcome(
            status=status,
            occurrence="occurred",
            cost={"usd_micros": 1},
            result_digest=digest,
            detail=detail,
        )


class CodeBindingProvider:
    """Namespaced binding provider for the 'code' domain (fs, patch, proc)."""

    @property
    def namespace(self) -> str:
        return "code"

    @property
    def supported_verbs(self) -> tuple[str, ...]:
        return (
            "fs.read",
            "fs.search",
            "fs.write",
            "patch.apply",
            "fs.patch",
            "proc.exec",
        )

    def create_adapter(self, verb: str, environment: Any, **kwargs: Any) -> CodeEffectAdapter:
        if verb not in self.supported_verbs:
            raise ValueError(f"Verb {verb!r} not supported by CodeBindingProvider")
        call_type = "observe" if verb in {"fs.read", "fs.search"} else "apply"
        return CodeEffectAdapter(verb, environment, call_type=call_type)
