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
from typing import Any, Callable, Sequence

__all__ = [
    "MODEL_PORTS",
    "ModelUnavailable",
    "SelectedModel",
    "select_model",
]

#: Selectable ports. `mock` is the default and the only one CI may rely on.
MODEL_PORTS = ("mock", "ollama", "openrouter", "deepseek")

#: Default local tag. Overridable, because whatever is pulled locally wins.
DEFAULT_OLLAMA_MODEL = "deepseek-r1"
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


def select_model(
    port: str = "mock",
    *,
    model_name: str | None = None,
    tape: Sequence[Any] = (),
    probe: Callable[[str], bool] | None = None,
    free_models: Callable[[], Sequence[str]] | None = None,
    env: Any = None,
) -> SelectedModel:
    """Return a labelled `ModelPort`, or raise `ModelUnavailable`.

    `probe` is injected so the decision is testable without a daemon; the
    default probes the real endpoint once. Probing once and failing closed is
    deliberate -- discovering the daemon is down on turn six wastes the turns
    before it and leaves a half-run in the corpus.
    """

    import os

    environ = env if env is not None else os.environ
    choice = (port or "mock").strip().lower()
    if choice not in MODEL_PORTS:
        raise ModelUnavailable(choice, f"unknown model port; expected one of {MODEL_PORTS}")

    if choice == "mock":
        from ..adapters.models.fake import FakeModel

        return SelectedModel(port="mock", model=FakeModel(list(tape)),
                             label="mock-scripted")

    if choice == "ollama":
        from ..adapters.models.ollama import OllamaModel

        name = model_name or DEFAULT_OLLAMA_MODEL
        endpoint = environ.get("VANGUARD_OLLAMA_ENDPOINT",
                               "http://127.0.0.1:11434/api/chat")
        if not (probe or _probe_http)(endpoint):
            raise ModelUnavailable("ollama", f"no daemon answering at {endpoint}")
        return SelectedModel(port="ollama",
                             model=OllamaModel(model=name, endpoint=endpoint),
                             label=f"ollama:{name}")

    if choice in {"openrouter", "deepseek"}:
        from ..adapters.models.openrouter import OpenRouterModel

        key = environ.get("OPENROUTER_API_KEY")
        if not key:
            raise ModelUnavailable(choice, "OPENROUTER_API_KEY is not set")
        allowed = list(free_models() if free_models is not None else _free_band())
        if not allowed:
            raise ModelUnavailable(
                choice, "no free-band models are registered; paid bands are "
                        "refused until S9-J-03 authorises spend")
        name = model_name or allowed[0]
        if name not in allowed:
            # The load-bearing refusal. A paid model reached by typo is still a
            # paid model, and the bill arrives either way.
            raise ModelUnavailable(
                choice, f"{name!r} is not in the free band; refusing to spend")
        return SelectedModel(port=choice, model=OpenRouterModel(model=name),
                             label=f"{choice}:{name}")

    raise ModelUnavailable(choice, "unreachable")


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


def _free_band() -> Sequence[str]:
    """Read the free band from the LAM registry. Never the `top` band."""
    import sys
    from pathlib import Path

    tools = Path(__file__).resolve().parents[3] / "tools" / "002_LLM_API_MOCK"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    try:
        from models import models_for_band  # type: ignore

        return list(models_for_band(FREE_BAND))
    except Exception:
        return []
