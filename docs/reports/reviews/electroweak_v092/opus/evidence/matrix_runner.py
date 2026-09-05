"""Harness-vs-model attribution matrix runner."""
import json, os, sys, time, pathlib, sqlite3, shutil

COND, MODEL_PORT, MODEL, TASK, WS = sys.argv[1:6]
MAXT = int(sys.argv[6]) if len(sys.argv) > 6 else 8

if COND == "fixed":
    from vanguard.packages.domain.models import profile as prof
    from vanguard.packages.domain.models.profile import ModelCapabilityProfile, ToolCallStyle
    for mid in (MODEL, "deepseek/deepseek-v4-flash-0731", "z-ai/glm-5.3-flash",
                "openrouter/free", "qwen2.5-coder:0.5b"):
        prof._PROFILES[mid] = ModelCapabilityProfile(
            mid, tool_call_style=ToolCallStyle.NATIVE,
            supports_system_role=True, supports_parallel_tool_calls=False)
    from vanguard.packages.kernel import policy as kp
    _o = kp.StandardPolicy.__init__
    def _p(self, *a, **kw):
        if kw.get("approval_required_above") == "low":
            kw["approval_required_above"] = "critical"
        return _o(self, *a, **kw)
    kp.StandardPolicy.__init__ = _p

TASKS = {
 "fib": ("Create a file fib.py in the workspace root that prints the first 10 "
         "Fibonacci numbers when run.", None),
 "calc": ("The test test_calculator.py fails. Fix the formula bug in "
          "src/calculator.py so all tests pass.", "t1-calculator"),
 "pandas": ("Create a file pipeline.py that reads data.csv with pandas, filters rows "
            "where value > 10, and prints the mean of the value column.", None),
}
brief, fixture = TASKS[TASK]
w = pathlib.Path(WS); shutil.rmtree(w, ignore_errors=True); w.mkdir(parents=True)
if fixture:
    fx = json.load(open(f"tools/002_LLM_API_MOCK/scenarios/{fixture}.json"))
    for p, c in fx["workspace"].items():
        f = w / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(c)
if TASK == "pandas":
    (w / "data.csv").write_text("name,value\na,5\nb,15\nc,25\nd,3\n")

from vanguard.packages.apps.coding_max.facade import CodingMaxFacade
t0 = time.time()
err = None
try:
    r = CodingMaxFacade(workspace=str(w)).run(
        brief=brief, preset="balanced", profile_id="local", model_port=MODEL_PORT,
        model=MODEL, max_turns=MAXT, interactive=False)
    d = r.to_dict() if hasattr(r, "to_dict") else dict(r.__dict__)
except Exception as e:
    d = {}; err = f"{type(e).__name__}: {e}"
wall = round(time.time() - t0, 1)

# workspace delta (exclude ledger + pyc pollution)
files = sorted(str(p.relative_to(w)) for p in w.rglob("*")
               if p.is_file() and ".vanguard" not in str(p) and "cache/python" not in str(p)
               and not str(p).endswith(".pyc"))
# ledger forensics
verbs, denials, effects = [], [], []
db = w / ".vanguard" / "events.sqlite3"
if db.exists():
    for (ej,) in sqlite3.connect(str(db)).execute("select envelope_json from events order by seq"):
        e = json.loads(ej); k = e.get("kind") or ""; p = e.get("payload", {})
        if k == "ProposalProduced": verbs.append(f"{p.get('action')}/{p.get('reason')}")
        elif k == "AuthorizationDenied": denials.append(p.get("reason"))
        elif k in ("EffectCompleted","EffectFailed","EffectReconciled"):
            effects.append(f"{k}:{p.get('action')}:{str(p.get('detail'))[:60]}")

# oracle
oracle = None
if TASK == "calc" and (w/"src"/"calculator.py").exists():
    import subprocess
    o = subprocess.run([sys.executable,"-m","pytest","-q","test_calculator.py"],
                       cwd=str(w), capture_output=True, text=True, timeout=60)
    oracle = "PASS" if o.returncode == 0 else "FAIL"
elif TASK == "fib" and (w/"fib.py").exists():
    import subprocess
    o = subprocess.run([sys.executable,"fib.py"], cwd=str(w), capture_output=True, text=True, timeout=30)
    got = o.stdout.split()
    oracle = "PASS" if got[:10] == "0 1 1 2 3 5 8 13 21 34".split() else f"FAIL:{o.stdout[:60]!r}"
elif TASK == "pandas" and (w/"pipeline.py").exists():
    oracle = "FILE_CREATED"

print(json.dumps({
 "condition": COND, "model_port": MODEL_PORT, "model": MODEL, "task": TASK,
 "terminal": d.get("terminalState"), "turns": d.get("turns"), "detail": d.get("detail"),
 "usage": d.get("tokenUsage"), "cost_micros": d.get("observedCost"),
 "wall_s": wall, "files": files, "oracle": oracle, "error": err,
 "proposals": verbs, "denials": denials, "effects": effects,
}, indent=1))
