"""Operator-facing credential status and live provider reachability.

Two questions the desktop Settings pane needs answered, neither of which the
UI can answer for itself once the gateway owns the secret (`SEC-01`):

  1. Can the runtime load `OPENROUTER_API_KEY` at all, and if not, exactly why?
  2. Does that key actually work against the provider right now?

Both answers are structural. Neither ever carries the secret value: the
status reports a *key reference* and a reason code, and the live probe reports
the provider's HTTP disposition. `load_api_key` stays the only reader of the
file, so the strict `.env` contract (regular file, mode 0600 or stricter,
untracked, no interpolation) is enforced on this path too.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from .env_loader import ALLOWED_KEY, load_api_key

__all__ = [
    "CREDENTIAL_STATES",
    "PROBE_MODEL",
    "credential_status",
    "probe_provider",
]

#: The states the Settings pane renders. `MISSING` and `DENIED` are distinct
#: on purpose: a key that is absent and a key the loader refuses to read need
#: different operator actions, and collapsing them produces the "I saved it and
#: nothing happened" report this endpoint exists to prevent.
CREDENTIAL_STATES = ("CONFIGURED", "MISSING", "DENIED", "INVALID")

#: Cheapest reachable model for a liveness probe. The probe asks for a single
#: token, so the call is a rounding error against any budget, but it exercises
#: the real inference path rather than a metadata endpoint that a
#: credit-exhausted key would still pass.
PROBE_MODEL = "openrouter/free"

_ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

_ERROR_STATE = {
    "not_found": "MISSING",
    "denied": "DENIED",
    "invalid_request": "INVALID",
}

_REMEDY = {
    "MISSING": (
        f"Add {ALLOWED_KEY}=<your key> to {{path}} and run: chmod 600 {{path}}"
    ),
    "DENIED": (
        f"{{path}} is readable by other users or is tracked by git. "
        "Run: chmod 600 {path}"
    ),
    "INVALID": f"{{path}} has a malformed or empty {ALLOWED_KEY} entry.",
}


def credential_status(root: str | os.PathLike[str]) -> dict[str, Any]:
    """Describe whether the runtime can load the provider key. Never the key."""
    env_path = Path(root) / ".env"
    result = load_api_key(root)

    if result.ok:
        return {
            "keyRef": ALLOWED_KEY,
            "state": "CONFIGURED",
            "source": str(env_path),
            "detail": "runtime can load the provider key",
            "remedy": "",
        }

    code = result.error.kind if result.error else "invalid_request"
    message = result.error.message if result.error else "load failed"
    state = _ERROR_STATE.get(code, "INVALID")
    return {
        "keyRef": ALLOWED_KEY,
        "state": state,
        "source": str(env_path),
        "detail": message,
        "remedy": _REMEDY[state].format(path=env_path),
    }


def probe_provider(
    root: str | os.PathLike[str],
    model: str = PROBE_MODEL,
    *,
    timeout: float = 20.0,
    transport: Callable[[str, dict[str, str], bytes, float], tuple[int, Mapping[str, str], bytes]]
    | None = None,
) -> dict[str, Any]:
    """Send a one-token completion and report what the provider said.

    `transport` is injectable so the test suite can exercise every disposition
    (401, 429, malformed body, transport failure) without a network or a key.
    """
    status = credential_status(root)
    if status["state"] != "CONFIGURED":
        return {
            "ok": False,
            "state": status["state"],
            "model": model,
            "detail": status["detail"],
            "remedy": status["remedy"],
        }

    secret = load_api_key(root).value or ""
    body = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 1,
        }
    ).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
    }

    send = transport
    if send is None:
        from .openrouter import _http_post

        def send(url, request_headers, payload, request_timeout):  # type: ignore[misc]
            return _http_post(url, request_headers, payload, timeout=request_timeout)

    try:
        code, _response_headers, raw = send(_ENDPOINT, headers, body, timeout)
    except Exception as exc:
        # The exception text can carry the URL but never the Authorization
        # header, so this is safe to surface; the secret is not in it.
        return {
            "ok": False,
            "state": "UNREACHABLE",
            "model": model,
            "detail": f"could not reach the provider: {exc}",
            "remedy": "Check network access to openrouter.ai and retry.",
        }

    if code == 200:
        return {
            "ok": True,
            "state": "CONFIGURED",
            "model": model,
            "detail": f"provider answered 200 for {model}",
            "remedy": "",
        }
    if code in (401, 403):
        return {
            "ok": False,
            "state": "INVALID",
            "model": model,
            "detail": f"provider rejected the key (HTTP {code})",
            "remedy": f"Replace {ALLOWED_KEY} in {Path(root) / '.env'} with a valid key.",
        }
    if code == 402:
        return {
            "ok": False,
            "state": "EXHAUSTED",
            "model": model,
            "detail": "provider reports no remaining credit (HTTP 402)",
            "remedy": "Add credit to the OpenRouter account, or select a free model.",
        }
    if code == 429:
        return {
            "ok": False,
            "state": "RATE_LIMITED",
            "model": model,
            "detail": "provider rate-limited the probe (HTTP 429)",
            "remedy": "Wait and retry.",
        }

    detail = f"provider returned HTTP {code}"
    try:
        parsed = json.loads(raw.decode("utf-8"))
        provider_message = parsed.get("error", {}).get("message")
        if provider_message:
            detail = f"{detail}: {provider_message}"
    except Exception:
        pass
    return {
        "ok": False,
        "state": "UNREACHABLE",
        "model": model,
        "detail": detail,
        "remedy": "Check the model id and the provider status page.",
    }
