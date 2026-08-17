import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from benchmarkings.guard import GuardRefusal, validate_run

RUNS = {
    "precondition": {"pre_passed": True},
    "no_intervention": {"effects_applied": 0, "post_passed": True, "prompt_tokens": 1},
    "not_invoked": {"effects_applied": 1, "prompt_tokens": 0, "completion_tokens": 0},
    "instrument": {"effects_applied": 1, "provider_error": True, "prompt_tokens": 1},
    "no_verdict": {"effects_applied": 1, "prompt_tokens": 1},
    "containment": {"effects_applied": 1, "prompt_tokens": 1, "verdict_present": True},
}

if __name__ == "__main__":
    run = RUNS[sys.argv[1]]
    if len(sys.argv) > 2 and sys.argv[2] == "--control":
        print(json.dumps({"passed": True}))
        raise SystemExit(0)
    try:
        validate_run(run)
    except GuardRefusal as exc:
        print(json.dumps({"refused": exc.reason}))
        raise SystemExit(1)
    raise SystemExit("guard accepted planted degenerate run")
