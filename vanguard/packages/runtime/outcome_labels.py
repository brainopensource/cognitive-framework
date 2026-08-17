"""Name why a run produced nothing (`S21-A-01`, `REQ-TRUST-001`).

`instrument_error` is a category, not a finding. Four different failures --
the provider never answered, the daemon timed out, the model emitted a shape
the translator refuses, the workspace was not there -- all reduced to the same
word, and a reader could not tell which had happened without opening the log.
Worse, each of them looked like the model scoring zero.

So a zero-turn run is labelled `instrument_error:<cause>`, and the cause comes
from the run's own detail rather than from a guess. An unrecognised detail is
`instrument_error:unclassified` and keeps the original text: inventing a
category for a message nobody has seen before is how a taxonomy starts lying.
"""

from __future__ import annotations

__all__ = ["INSTRUMENT_CAUSES", "classify_instrument_error"]

#: detail fragment -> cause slug. Ordered: the first match wins, so more
#: specific fragments precede the general ones.
INSTRUMENT_CAUSES: tuple[tuple[str, str], ...] = (
    # The model answered, but with several tool calls in one turn. One turn is
    # one effect, so the translator refuses -- correctly. This is a harness
    # constraint meeting an over-eager model, not a model failing the task.
    ("multiple actions in one proposal", "multi_action_proposal"),
    # The model asked for a path outside the workspace. Containment refused,
    # correctly -- but this is a *model* mistake, not a provider fault, and
    # lumping it with transport errors hid how often models try it.
    ("escapes workspace", "path_escape_refused"),
    ("streaming response was malformed", "provider_malformed_response"),
    ("truncated, or empty", "provider_malformed_response"),
    ("timed out", "provider_timeout"),
    ("timeout", "provider_timeout"),
    ("is not pulled", "model_tag_absent"),
    ("no daemon answering", "provider_unreachable"),
    ("api_key", "provider_key_missing"),
    ("not in the free band", "paid_model_refused"),
    ("refusing to spend", "paid_model_refused"),
    ("http 5", "provider_server_error"),
    ("http 4", "provider_request_rejected"),
    ("malformed json", "malformed_proposal"),
    ("tool arguments", "malformed_proposal"),
    ("is not declared by manifest", "undeclared_tool"),
    ("unsupported action", "undeclared_tool"),
    ("scripted model exhausted", "tape_exhausted"),
    # Last: the provider produced no proposal at all. Only correct when
    # nothing more specific matched, which is why it sits at the bottom.
    ("model_not_invoked", "model_not_invoked"),
)


def classify_instrument_error(detail: str | None) -> str:
    """Return `instrument_error:<cause>` for a run that produced no turn."""
    text = (detail or "").strip().lower()
    if not text:
        return "instrument_error:unclassified"
    for fragment, cause in INSTRUMENT_CAUSES:
        if fragment in text:
            return f"instrument_error:{cause}"
    return "instrument_error:unclassified"
