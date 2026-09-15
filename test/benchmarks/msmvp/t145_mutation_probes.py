"""T-145 probe table: are the `E4` ingress controls real controls?

`DIR-5.5` is binding on every negative control T-145 introduces, and §7.4 makes
the procedure explicit. These probes disable each guard the T-145 repair added
and require the control that names it to red. The procedure lives in
`_mutation.py`; this module is only the table.

NOT PROVED HERE -- `E-CLI-1`(a), the workspace-identity guard itself. The
crash (`E-CLI-1`(b)) is closed and proved by probe 3. But no route-level
control can isolate a guard on workspace *identity*: a plain directory is
unobservable and unindexable at once, so `INDEX_UNBOUND` refuses first, and a
run under a scripted `finish`-only model is independently refused for want of
verification and changed-file evidence. Isolating it needs a journey that
would otherwise complete -- `T-146`/`E5`. Probes numbered 1, 2 and 7 were
attempted against a `workspace_repository_present` guard and withdrawn: the
guard red 6 controls across T-141 and INDEX_UNBOUND because it asked git
directly from the session, asserting one adapter's implementation at a port
boundary. Recorded, not silently dropped.

Run:
    python3 -m test.benchmarks.msmvp.t145_mutation_probes
    python3 -m test.benchmarks.msmvp.t145_mutation_probes --json
"""
from __future__ import annotations

import sys

from ._mutation import ENTRYPOINT, REPO_ROOT, Probe, main

TASK_STATE = REPO_ROOT / "vanguard/packages/runtime/task_state.py"

_SUITE = (
    "test.falsifiers.test_t145_public_ingress_truthfulness",
    "test.runtime.test_app_service_and_cli",
)


PROBES: tuple[Probe, ...] = (
    Probe(
        key="3",
        clause="E4: a refusal is a terminal, not a traceback",
        guard="the typed-terminal catch at the public route",
        edits=((
            ENTRYPOINT,
            "    except (WorkspaceSnapshotRefused, ContextPacketError) as refused:\n",
            "    except (_NeverRaised,) as refused:\n",
        ),),
        expects=("plain_directory", "changed_preset", "app_service"),
    ),
    Probe(
        key="4",
        clause="E-CLI-2: hydration is keyed on durable state",
        guard="the `if events:` hydration condition (restore the command verb)",
        edits=((
            ENTRYPOINT,
            "    if events:\n"
            "        resumed = fold_task_state(events, objective=brief)\n",
            '    if events and command == "resume":\n'
            "        resumed = fold_task_state(events, objective=brief)\n",
        ),),
        expects=("hydrates_a_run", "turn_ceiling", "ceiling"),
    ),
    Probe(
        key="5",
        clause="E-CLI-2: revalidate rather than trust",
        guard="the turn-ceiling revalidation at the ingress",
        edits=((
            ENTRYPOINT,
            "        if durable_turns is not None and max_turns > durable_turns:\n",
            "        if False:\n",
        ),),
        expects=("turn_ceiling", "ceiling"),
    ),
    Probe(
        key="6",
        clause="E-CLI-2: widened hydration does not weaken resume",
        guard="the explicit `resume` refusal when no durable events exist",
        edits=((
            ENTRYPOINT,
            '    if command == "resume" and not events:\n'
            '        raise ValueError(f"resume state unavailable: no durable events for {run_id}")\n',
            "",
        ),),
        expects=("resume_with_no_durable_events",),
    ),
    Probe(
        key="8",
        clause="E-CLI-2: composition revalidation is reachable at all",
        guard="the merge-not-replace of selectionPolicyIdentity in task_state",
        edits=((
            TASK_STATE,
            "                merged = dict(state.get(\"selectionPolicyIdentity\") or {})\n"
            "                merged.update(payload[\"selectionPolicyIdentity\"])\n"
            "                state[\"selectionPolicyIdentity\"] = merged\n",
            "                state[\"selectionPolicyIdentity\"] = dict(\n"
            "                    payload[\"selectionPolicyIdentity\"])\n",
        ),),
        expects=("changed_preset",),
    ),
    Probe(
        key="9",
        clause="E4: a fail-closed refusal is a terminal, not a traceback",
        guard="the ContextPacketError arm of the entrypoint typed terminal",
        edits=((
            ENTRYPOINT,
            "    except (WorkspaceSnapshotRefused, ContextPacketError) as refused:\n",
            "    except (WorkspaceSnapshotRefused,) as refused:\n",
        ),),
        expects=("changed_preset",),
    ),
)


if __name__ == "__main__":
    raise SystemExit(main(PROBES, _SUITE, sys.argv[1:]))
