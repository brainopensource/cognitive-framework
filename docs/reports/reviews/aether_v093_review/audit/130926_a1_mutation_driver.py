"""Revert each A1 guard in place, show the falsifier reds, restore."""
import pathlib, subprocess, sys

ROOT = pathlib.Path("/home/rock-dev/Coding/cognitive-framework")
ENGINE = ROOT / "vanguard/packages/agency/episode/engine.py"
OBS = ROOT / "vanguard/packages/agency/episode/observation.py"

MUTATIONS = [
    ("M1 read-only membership", ENGINE,
     """        mutating = [request.action for request in proposal.observations
                    if not self._is_observation(request.action)]""",
     """        mutating = []"""),
    ("M2 fail-closed on undeclared sinks", ENGINE,
     """        if self._observation_sinks is None:
            return ("this composition has not declared which of its verbs are "
                    "observations, so it settles no parallel batches.")""",
     """        if self._observation_sinks is None:
            return None"""),
    ("M3 descriptor keyed on provider ids", OBS,
     """                "dependsOn": sorted(index_of[dep] for dep in request.depends_on
                                    if dep in index_of),""",
     """                "requestId": request.request_id,
                "dependsOn": list(request.depends_on),"""),
    ("M4 settlement ignores dependencies", OBS,
     """    pending = {
        position: {index_of[dep] for dep in request.depends_on if dep in index_of}
        for position, request in enumerate(requests)
    }""",
     """    pending = {position: set() for position, _ in enumerate(requests)}"""),
    ("M5 batch aborts on the first failing member", ENGINE,
     """                if _TERMINAL_FOR_FAILURE.get(outcome.failure) is not None:
                    halting = outcome
                    break""",
     """                if outcome.failure is not FailurePath.OK:
                    halting = outcome
                    break"""),
    ("M6 no batch ceiling", OBS,
     """    if len(rows) > MAX_PARALLEL_OBSERVATIONS:
        raise ValueError(
            f"{len(rows)} requests exceeds the parallel observation ceiling "
            f"of {MAX_PARALLEL_OBSERVATIONS}")""",
     """    pass"""),
    ("M8 phase gate generalised to batches", ENGINE,
     """            if proposal.kind is ProposalKind.OBSERVE:
                requested_actions = [request.action
                                     for request in proposal.observations]
            elif proposal.kind == ProposalKind.EFFECT:""",
     """            if False:
                requested_actions = []
            elif proposal.kind == ProposalKind.EFFECT:"""),
    ("M7 attenuated child scope refusal", ENGINE,
     """        if self._attenuated:
            outside = [request.action for request in proposal.observations
                       if request.action not in self._scope.actions]
            if outside:
                return (f"{', '.join(sorted(set(outside)))} is outside this "
                        "episode's sealed scope.")""",
     """        if False:
            pass"""),
]

def red(label):
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "test.falsifiers.test_parallel_observation"],
        cwd=ROOT, capture_output=True, text=True, timeout=300)
    tail = [l for l in proc.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:", "Ran ", "OK", "FAILED"))]
    print(f"  {label}: " + " | ".join(tail[-2:]))
    return proc.returncode != 0, [l for l in proc.stderr.splitlines() if l.startswith(("FAIL:", "ERROR:"))]

print("BASELINE (must be green):")
ok, _ = red("baseline")
assert not ok, "baseline is not green"

for name, path, original, mutant in MUTATIONS:
    text = path.read_text()
    if original not in text:
        print(f"  {name}: ANCHOR NOT FOUND -- mutation not applied")
        continue
    path.write_text(text.replace(original, mutant, 1))
    try:
        failed, names = red(name)
        status = "RED" if failed else "!!! STILL GREEN !!!"
        print(f"    -> {status}")
        for n in names[:6]:
            print(f"       {n}")
    finally:
        path.write_text(text)

print("RESTORED (must be green again):")
red("restored")
