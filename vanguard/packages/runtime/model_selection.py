"""Choose a `ModelPort` for a driver run, and fail closed when it is absent.

`REQ-TRUST-001`. The default is MOCK because CI must have a brain that is free,
offline and deterministic. Everything else is opt-in and **probed once** before
a run starts: a backend that is not there produces a named `instrument_error`,
never a skipped test that reports success.

The distinction this module exists to hold: *skip-closed* and *skip-as-pass*
look identical in a summary and mean opposite things. A run whose provider was
never reachable produced no measurement, so it is inconclusive; calling it a
pass would put a number in the corpus that no model produced.

**Free only.** OpenRouter selection refuses any model outside the `free` band
until `S9-J-03` authorises spend. There is no fourth HTTP client here -- each
branch returns an adapter that already exists in the tree.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

__all__ = [
    "MODEL_PORTS",
    "ModelUnavailable",
    "SelectedModel",
    "inspect_model_providers",
    "select_model",
    "get_default_model",
    "get_default_paid_model",
    "get_pricing_usd_table",
    "resolve_model",
    "load_model_registry",
]

#: Selectable ports. `mock` and `fake` are deterministic and offline.
MODEL_PORTS = ("mock", "fake", "cassette", "lam", "ollama", "openrouter", "deepseek", "router")

#: Default local tag. Overridable, because whatever is pulled locally wins.
DEFAULT_OLLAMA_MODEL = "deepseek-r1"
#: Local reasoning models emit a long think block before their first token, and
#: a 60s ceiling turned that into `instrument_error: timed out` on the larger
#: briefs -- an instrument failure that reads like a model scoring zero.
DEFAULT_LOCAL_TIMEOUT_SECONDS = 300.0
#: OpenRouter free routes are capacity-queued; 30s made the TUI look idle.
DEFAULT_OPENROUTER_TIMEOUT_SECONDS = 120.0
#: `D-13` / `S7-C-06`: `top` is empty until the Project Lead names ids.
FREE_BAND = "free"


class ModelUnavailable(RuntimeError):
    """A named reason a backend cannot be used. Carries the instrument error."""

    def __init__(self, port: str, reason: str) -> None:
        super().__init__(f"{port}: {reason}")
        self.port = port
        self.reason = reason
        #: What the session should record. Never "ok", never silence.
        self.instrument_error = f"instrument_error:{port}_unavailable"


@dataclass(frozen=True, slots=True)
class SelectedModel:
    """The chosen port, labelled so the log says which brain ran."""

    port: str
    model: Any
    label: str

    def to_dict(self) -> dict[str, str]:
        return {"modelPort": self.port, "modelLabel": self.label}


def _find_env_key(key_name: str, environ: Any) -> str | None:
    if hasattr(environ, "get"):
        val = environ.get(key_name)
        if val:
            return str(val)
    # Provider credentials are an explicit process/caller input.  Runtime
    # selection must never discover a repository .env on its own: doing so
    # turns otherwise hermetic tests into paid network runs.  Product entry
    # points that support dotenv load it deliberately before selecting a port.
    return None


def select_model(
    port: str = "mock",
    *,
    model_name: str | None = None,
    models: Sequence[str] | None = None,
    tape: Sequence[Any] = (),
    timeout_seconds: float | None = None,
    probe: Callable[[str], bool] | None = None,
    free_models: Callable[[], Sequence[str]] | None = None,
    env: Any = None,
    allow_paid: bool = False,
    reasoning_effort: str | None = None,
) -> SelectedModel:
    """Return a labelled `ModelPort`, or raise `ModelUnavailable`.

    `probe` is injected so the decision is testable without a daemon; the
    default probes the real endpoint once. Probing once and failing closed is
    deliberate -- discovering the daemon is down on turn six wastes the turns
    before it and leaves a half-run in the corpus.
    """
    import os

    environ = env if env is not None else os.environ
    paid_allowed = allow_paid or (str(environ.get("VANGUARD_ALLOW_PAID", "")).strip().lower() in {"1", "true", "yes"})
    choice = (port or "mock").strip().lower()
    if choice not in MODEL_PORTS:
        raise ModelUnavailable(choice, f"unknown model port; expected one of {MODEL_PORTS}")

    if choice in {"mock", "fake"}:
        from ..adapters.models.fake import FakeModel

        tape_list = list(tape) if tape else [{"kind": "finish", "note": f"{choice}-default"}]
        return SelectedModel(
            port=choice,
            model=FakeModel(tape_list),
            label=f"{choice}-scripted",
        )

    if choice == "cassette":
        from ..adapters.models.cassette import Cassette, CassettePlayer

        return SelectedModel(
            port="cassette",
            model=CassettePlayer(Cassette(list(tape))),
            label="cassette-player",
        )

    if choice == "lam":
        from ..adapters.models.openrouter import OpenRouterModel

        base_url = environ.get("LAM_BASE_URL", "http://127.0.0.1:8787")
        endpoint = f"{base_url.rstrip('/')}/v1/chat/completions"
        target_model = model_name or "lam/t1-calculator"
        if probe is not None:
            if not probe(f"{base_url}/health"):
                raise ModelUnavailable("lam", f"no daemon answering at {base_url}")
        else:
            if not _probe_http(f"{base_url}/health"):
                raise ModelUnavailable("lam", f"no daemon answering at {base_url}")

        model = OpenRouterModel(
            endpoint=endpoint,
            model=target_model,
            mode="replay",
            provider="lam",
            api_key_ref="LAM_MOCK_KEY",
            environ={"LAM_MOCK_KEY": "sk-lam-mock-key"},
            stream=False,
        )
        return SelectedModel(port="lam", model=model, label=f"lam:{target_model}")

    if choice == "ollama":
        from ..adapters.models.ollama import OllamaModel

        endpoint = environ.get("VANGUARD_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat")
        if probe is not None:
            name = model_name or DEFAULT_OLLAMA_MODEL
            if not probe(endpoint):
                raise ModelUnavailable("ollama", f"no daemon answering at {endpoint}")
        else:
            installed = _ollama_tags(endpoint)
            if not installed:
                raise ModelUnavailable("ollama", f"no daemon answering at {endpoint}")
            name = _resolve_tag(model_name or DEFAULT_OLLAMA_MODEL, installed)
            if name is None:
                raise ModelUnavailable(
                    "ollama",
                    f"{model_name or DEFAULT_OLLAMA_MODEL!r} is not pulled; "
                    f"installed: {', '.join(sorted(installed))}",
                )
        return SelectedModel(
            port="ollama",
            model=OllamaModel(
                model=name,
                endpoint=endpoint,
                timeout_seconds=timeout_seconds or DEFAULT_LOCAL_TIMEOUT_SECONDS,
            ),
            label=f"ollama:{name}",
        )

    if choice in {"openrouter", "deepseek"}:
        from ..adapters.models.openrouter import OpenRouterModel

        key = _find_env_key("OPENROUTER_API_KEY", environ)
        if not key:
            raise ModelUnavailable(choice, "OPENROUTER_API_KEY is not set")
        openrouter_timeout = timeout_seconds or DEFAULT_OPENROUTER_TIMEOUT_SECONDS
        openrouter_environ = dict(environ) if environ is not None else None
        if paid_allowed or models:
            if not model_name:
                allowed = list(free_models() if free_models is not None else _free_band())
                name = allowed[0] if allowed else _get_default_paid_model()
            else:
                try:
                    name = resolve_model(model_name)
                except (ModelPolicyError, ValueError) as exc:
                    raise ModelUnavailable(choice, f"model {model_name!r} is not authorized in models_registry.json: {exc}") from exc
            stream_choice = False if "deepseek" in (name or "") else True
            effort_choice = reasoning_effort or ("none" if "deepseek" in (name or "") else None)
            return SelectedModel(
                port=choice,
                model=OpenRouterModel(
                    model=name,
                    models=models,
                    stream=stream_choice,
                    reasoning_effort=effort_choice,
                    request_timeout=openrouter_timeout,
                    environ=openrouter_environ,
                ),
                label=f"{choice}:{name}",
            )

        allowed = list(free_models() if free_models is not None else _free_band())
        if not allowed:
            raise ModelUnavailable(
                choice,
                "no free-band models are registered; paid bands are refused until S9-J-03 authorises spend",
            )
        raw_name = model_name or allowed[0]
        # A caller-supplied free-band provider is an injected authority (used
        # by offline tests and local routers), so its opaque model IDs must be
        # accepted without requiring them to exist in the production registry.
        # Resolve aliases only when the name is not already in that band; an
        # explicitly named model outside the band must retain the spend
        # refusal, rather than leaking a registry-validation error.
        if raw_name in allowed:
            name = raw_name
        else:
            try:
                name = resolve_model(raw_name)
            except (ModelPolicyError, ValueError) as exc:
                raise ModelUnavailable(choice, f"{raw_name!r} is not in the free band; refusing to spend") from exc
        if name not in allowed:
            raise ModelUnavailable(choice, f"{name!r} is not in the free band; refusing to spend")
        stream_choice = False if "deepseek" in (name or "") else True
        effort_choice = reasoning_effort or ("none" if "deepseek" in (name or "") else None)
        return SelectedModel(
            port=choice,
            model=OpenRouterModel(
                model=name,
                models=models,
                stream=stream_choice,
                reasoning_effort=effort_choice,
                request_timeout=openrouter_timeout,
                environ=openrouter_environ,
            ),
            label=f"{choice}:{name}",
        )

    if choice == "router":
        from ..adapters.models.openrouter import OpenRouterModel

        key = environ.get("OPENROUTER_API_KEY")
        if not key:
            raise ModelUnavailable(choice, "OPENROUTER_API_KEY is not set")
        openrouter_timeout = timeout_seconds or DEFAULT_OPENROUTER_TIMEOUT_SECONDS
        openrouter_environ = dict(environ) if environ is not None else None
        if paid_allowed:
            if not model_name:
                allowed = list(free_models() if free_models is not None else _free_band())
                name = allowed[0] if allowed else _get_default_paid_model()
            else:
                try:
                    name = resolve_model(model_name)
                except (ModelPolicyError, ValueError) as exc:
                    raise ModelUnavailable(choice, f"model {model_name!r} is not authorized in models_registry.json: {exc}") from exc
            return SelectedModel(
                port="router",
                model=OpenRouterModel(
                    model=name,
                    stream=False,
                    reasoning_effort="none",
                    request_timeout=openrouter_timeout,
                    environ=openrouter_environ,
                ),
                label=f"router:{name}",
            )

        allowed = list(free_models() if free_models is not None else _free_band())
        if not allowed:
            raise ModelUnavailable(choice, "no free-band models are registered")
        name = model_name or allowed[0]
        if name not in allowed:
            raise ModelUnavailable(choice, f"{name!r} is not in the free band; refusing to spend")
        return SelectedModel(
            port="router",
            model=OpenRouterModel(
                model=name,
                stream=False,
                reasoning_effort="none",
                request_timeout=openrouter_timeout,
                environ=openrouter_environ,
            ),
            label=f"router:{name}",
        )

    raise ModelUnavailable(choice, "unreachable")


def inspect_model_providers(env: Any = None) -> list[dict[str, Any]]:
    """Safe diagnostic report of provider readiness without leaking credentials."""
    import os

    environ = env if env is not None else os.environ
    has_or_key = bool(environ.get("OPENROUTER_API_KEY"))
    has_ds_key = bool(environ.get("DEEPSEEK_API_KEY"))
    ollama_ep = environ.get("VANGUARD_OLLAMA_ENDPOINT", "http://127.0.0.1:11434/api/chat")

    return [
        {
            "port": "mock",
            "readiness": "ready",
            "detail": "offline deterministic test double",
            "hasCredentials": True,
        },
        {
            "port": "fake",
            "readiness": "ready",
            "detail": "offline scripted test double",
            "hasCredentials": True,
        },
        {
            "port": "cassette",
            "readiness": "ready",
            "detail": "offline deterministic cassette replay",
            "hasCredentials": True,
        },
        {
            "port": "openrouter",
            "readiness": "ready" if has_or_key else "unconfigured",
            "detail": "configured with API key" if has_or_key else "OPENROUTER_API_KEY missing",
            "hasCredentials": has_or_key,
        },
        {
            "port": "deepseek",
            "readiness": "ready" if (has_ds_key or has_or_key) else "unconfigured",
            "detail": "configured with API key" if (has_ds_key or has_or_key) else "DEEPSEEK_API_KEY/OPENROUTER_API_KEY missing",
            "hasCredentials": bool(has_ds_key or has_or_key),
        },
        {
            "port": "ollama",
            "readiness": "configured",
            "detail": f"endpoint: {ollama_ep}",
            "hasCredentials": True,
        },
    ]


def _probe_http(endpoint: str) -> bool:
    """One cheap reachability check. Any failure is a failure."""
    import urllib.error
    import urllib.request

    root = endpoint.split("/api/")[0]
    try:
        with urllib.request.urlopen(root, timeout=2.0) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except Exception:
        return False


def _ollama_tags(endpoint: str) -> tuple[str, ...]:
    """Tags the daemon actually has. Empty means unreachable or empty."""
    import json
    import urllib.request

    root = endpoint.split("/api/")[0]
    try:
        with urllib.request.urlopen(f"{root}/api/tags", timeout=3.0) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return ()
    models = payload.get("models")
    if not isinstance(models, list):
        return ()
    return tuple(
        str(entry.get("name", ""))
        for entry in models
        if isinstance(entry, dict) and entry.get("name")
    )


def _resolve_tag(wanted: str, installed: Sequence[str]) -> str | None:
    if wanted in installed:
        return wanted
    prefix = f"{wanted.split(':')[0]}:"
    matches = sorted(tag for tag in installed if tag.startswith(prefix))
    return matches[0] if matches else None


from ..adapters.models.config import (
    get_band_models,
    get_default_model,
    get_default_paid_model,
    get_pricing_usd_table,
    load_model_registry,
    resolve_model,
    ModelPolicyError,
)


def _free_band() -> Sequence[str]:
    """Read the free band from the models registry. Never the `top` band."""
    return get_band_models("free")


def _get_default_paid_model() -> str:
    return get_default_paid_model()
