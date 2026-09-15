"""T-147 probe table: does each T-141 negative control actually red?

The eight probes `docs/execution/main/mvp_delivery_protocol.md` §6 (T-147)
makes mandatory. The procedure itself lives in `_mutation.py`; this module is
only the table of guards and the controls that must name them.

Run:
    python3 -m test.benchmarks.msmvp.t147_mutation_probes
    python3 -m test.benchmarks.msmvp.t147_mutation_probes --json
"""
from __future__ import annotations

import sys

from ._mutation import CHILD_RUNTIME, WORKSPACE, Probe, main

_SUITE = (
    "test.falsifiers.test_t141_child_workspace_lifecycle",
    "test.falsifiers.test_t141_production_activation",
)


PROBES: tuple[Probe, ...] = (
    Probe(
        key="a",
        clause="C-PUB-5 (Base)",
        guard="base revalidation in _require_current_base",
        edits=((
            WORKSPACE,
            '        current = self.shared_digest()\n'
            '        if current != base["digest"]:\n',
            '        current = self.shared_digest()\n'
            '        if False:\n',
        ),),
        expects=("stale",),
    ),
    Probe(
        key="b",
        clause="C-PUB-5 (Verdict), defence in depth",
        guard="BOTH verdict-pass checks (publish + _authorization)",
        edits=(
            (
                WORKSPACE,
                "        if not verdict.passed():\n",
                "        if False:\n",
            ),
            (
                WORKSPACE,
                '        if str(verdict.get("disposition") or "").strip().lower() not in {\n'
                '            "pass", "passed"\n'
                '        }:\n',
                "        if False:\n",
            ),
        ),
        expects=("verdict", "unverified", "rejected", "undeterminable"),
    ),
    Probe(
        key="c",
        clause="C-PUB-7 (recovery finishes, never decides)",
        guard="recovery's authorization requirement",
        edits=((
            WORKSPACE,
            "            record = self._authorization(child_id)\n"
            "            if record is None:\n"
            "                continue\n",
            "            record = self._authorization(child_id)\n"
            "            if False:\n"
            "                continue\n",
        ),),
        expects=("recovery",),
    ),
    Probe(
        key="d",
        clause="C-PUB-5 (Verdict) / C-PUB-6",
        guard="signed-subject binding check in _verify_tree",
        edits=((
            CHILD_RUNTIME,
            "        if signed_subject != combined.digest:\n",
            "        if False:\n",
        ),),
        expects=("verified", "tree", "publish"),
    ),
    Probe(
        key="e",
        clause="C-PUB-1 (child-local effects)",
        guard="child-local adapter requirement in _environment_for",
        edits=((
            CHILD_RUNTIME,
            "        if self._child_environment is None:\n"
            "            raise PublicationRefused(\n"
            '                "T-141: a supervised child needs a child-local effect adapter; "\n'
            '                "refusing to run it against the parent\'s environment")\n',
            "        if self._child_environment is None:\n"
            "            return self._parent_ports.environment\n",
        ),),
        expects=("adapter", "environment", "contain"),
    ),
    Probe(
        key="f",
        clause="C-PUB-5 (authority)",
        guard="authority recheck in _publish",
        edits=((
            CHILD_RUNTIME,
            "            lapsed = authority.recheck(plan, projected.actual_cost)\n"
            "            if lapsed:\n",
            "            lapsed = authority.recheck(plan, projected.actual_cost)\n"
            "            if False:\n",
        ),),
        expects=("grant", "authority"),
    ),
    Probe(
        key="g",
        clause="C-PUB-8 (forbidden targets)",
        guard="repository-metadata target refusal in _shared_target",
        edits=((
            WORKSPACE,
            "        if EXCLUDED_DIRNAMES.intersection(candidate.parts):\n",
            "        if False:\n",
        ),),
        expects=("metadata",),
    ),
    Probe(
        key="h",
        clause="C-PUB-8 (base exclusion moves with target refusal)",
        guard="repository-metadata base exclusion in shared_entries",
        edits=((
            WORKSPACE,
            "            if EXCLUDED_DIRNAMES.intersection(relative.parts[:-1]):\n",
            "            if False:\n",
        ),),
        expects=("metadata",),
    ),
)


if __name__ == "__main__":
    raise SystemExit(main(PROBES, _SUITE, sys.argv[1:]))
