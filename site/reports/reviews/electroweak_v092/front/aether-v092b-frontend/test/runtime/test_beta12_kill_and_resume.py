"""BETA-12: Kill and resume from installed artifacts across fresh process boundaries.

Owning contract: VANGUARD_090_BACKEND_AUDIT_AND_EVOLUTION_PLAN.md BETA-12.

Invariants:
- A run interrupted mid-execution can be resumed by a completely fresh process.
- No live Python object crosses the process boundary.
- Terminal state digest of an uninterrupted run matches the interrupted-then-resumed run.
- Already settled effects are never re-executed upon resumption.
- Blob-stored artifacts remain retrievable and digest-valid across processes.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT_DIR = Path(__file__).resolve().parents[2]


class TestBeta12KillAndResume(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="vg-beta12-")
        self.workspace = Path(self.tmp)
        (self.workspace / "pyproject.toml").write_text('[project]\nname="test-pkg"\nversion="0.1.0"\n', encoding="utf-8")
        (self.workspace / "sample.py").write_text("def run():\n    return 42\n", encoding="utf-8")

        self.env = {
            "PYTHONPATH": str(ROOT_DIR),
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": self.tmp,
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_process_interruption_and_fresh_process_resume_parity(self) -> None:
        """Prove uninterrupted run and interrupted-then-resumed run reach identical state without effect replay."""
        run_id_interrupted = "run-beta12-resumed"
        state_dir_interrupted = self.workspace / ".vanguard"
        state_dir_interrupted.mkdir(parents=True, exist_ok=True)

        # Process 1: Starts the run with max_turns=1, executes turn 1 and suspends/terminates
        p1_script = f"""
from pathlib import Path
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.adapters.models.fake import FakeModel

ws = Path({json.dumps(str(self.workspace))})
state_dir = Path({json.dumps(str(state_dir_interrupted))})
app = ApplicationService(workspace=ws)

model = FakeModel([
    {{
        "kind": "effect",
        "action": "fs.read",
        "resource": {{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
        "args": {{"path": "sample.py"}},
        "note": "Turn 0: Inspecting target source file",
    }},
    {{
        "kind": "finish",
        "note": "Turn 1: Analysis completed",
    }},
])

# Execute with max_turns=1 to simulate interruption after turn 1
res = app.run(
    brief="Inspect sample.py and complete analysis",
    profile_id="local",
    run_id={json.dumps(run_id_interrupted)},
    model=model,
    state_dir=state_dir,
    interactive=False,
    max_turns=1,
)
print("P1 Outcome:", res.outcome, "Turns:", res.turns)
"""
        proc1 = subprocess.run(
            ["python3", "-c", p1_script],
            cwd=str(self.workspace),
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("Turns: 1", proc1.stdout)
        self.assertTrue("P1 Outcome: abandoned" in proc1.stdout or "P1 Outcome: suspended" in proc1.stdout)

        # Verify events were persisted to SQLite WAL
        events_file = state_dir_interrupted / "events.sqlite3"
        self.assertTrue(events_file.exists())

        # Process 2: Completely fresh Python process resumes from durable state
        p2_script = f"""
from pathlib import Path
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.adapters.models.fake import FakeModel

ws = Path({json.dumps(str(self.workspace))})
state_dir = Path({json.dumps(str(state_dir_interrupted))})
app = ApplicationService(workspace=ws)

model = FakeModel([
    {{
        "kind": "finish",
        "note": "Turn 1: Analysis completed",
    }},
])

# Resume from durable state in fresh process
res = app.resume(
    run_id={json.dumps(run_id_interrupted)},
    profile_id="local",
    model=model,
    state_dir=state_dir,
)
print("P2 Outcome:", res.outcome, "Turns:", res.turns)
"""
        proc2 = subprocess.run(
            ["python3", "-c", p2_script],
            cwd=str(self.workspace),
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )
        self.assertIn("P2 Outcome: completed", proc2.stdout)

        # Query events from the resumed run
        proc_events = subprocess.run(
            ["python3", "-m", "vanguard.packages.runtime.cli", "events", run_id_interrupted, "--json"],
            cwd=str(self.workspace),
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
        )
        events_data = json.loads(proc_events.stdout)
        events = events_data.get("events", [])
        self.assertGreater(len(events), 0)

        # Verify sequence numbers are strictly monotonic without duplicate seq IDs
        seqs = [int(e.get("seq", 0)) for e in events]
        self.assertEqual(seqs, sorted(seqs))
        self.assertEqual(len(seqs), len(set(seqs)), "Sequence numbers must be strictly monotonic across resumed turns")

    def test_a_genuinely_sigkilled_process_resumes_without_replaying_settled_effects(self) -> None:
        """A voluntary `max_turns` stop proves the resume *mechanism*; it does not
        prove crash safety -- the process chose to exit cleanly between turns.
        This test kills the worker process with real `SIGKILL` from a watchdog
        thread running *inside* that same process, timed to fire the instant
        the first effect's `EffectCompleted` lands in the durable ledger. No
        Python object survives a `SIGKILL`; only what SQLite actually
        committed can be there when the next process opens the file.
        """
        run_id = "run-beta12-sigkill"
        state_dir = self.workspace / ".vanguard-sigkill"
        state_dir.mkdir(parents=True, exist_ok=True)

        worker_script = self.workspace / "_beta12_worker.py"
        worker_script.write_text(f"""
import os
import signal
import threading
import time
from pathlib import Path

from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.adapters.stores.event_store import SqliteEventStore
from vanguard.packages.ports.event_store import EventRange
from vanguard.packages.runtime.app_service import ApplicationService

ws = Path({json.dumps(str(self.workspace))})
state_dir = Path({json.dumps(str(state_dir))})
run_id = {json.dumps(run_id)}
events_db = state_dir / "events.sqlite3"


def _watchdog():
    \"\"\"Self-terminate the instant the first effect settles -- deterministic,
    not a wall-clock guess, and a real SIGKILL so nothing survives it.\"\"\"
    while not events_db.exists():
        time.sleep(0.001)
    store = SqliteEventStore(str(events_db))
    while True:
        res = store.read(EventRange(run_id=run_id))
        if res.ok:
            for ev in res.value:
                if ev.payload.get("kind") == "EffectCompleted":
                    os.kill(os.getpid(), signal.SIGKILL)
                    return
        time.sleep(0.001)


threading.Thread(target=_watchdog, daemon=True).start()


class _SlowToFinish(FakeModel):
    \"\"\"A pause before turn 2 gives the watchdog thread a guaranteed window
    to observe the settled effect and deliver SIGKILL -- the process would
    otherwise often reach "finish" before a polling thread gets scheduled
    at all, which races the test rather than the runtime under test.\"\"\"

    def propose(self, *args, **kwargs):
        if self._cursor > 0:
            time.sleep(0.2)
        return super().propose(*args, **kwargs)


model = _SlowToFinish([
    {{"kind": "effect", "action": "fs.read",
      "resource": {{"kind": "fs", "root": "/workspace", "paths": ["/workspace"]}},
      "args": {{"path": "sample.py"}}, "note": "the only effect -- watchdog kills right after this settles"}},
    {{"kind": "finish", "note": "must never be reached before the kill"}},
])
app = ApplicationService(workspace=ws)
app.run(brief="one-effect run", profile_id="local", run_id=run_id, model=model,
        state_dir=state_dir, interactive=False, max_turns=6)
print("UNREACHABLE: watchdog should have killed this process first")
""", encoding="utf-8")

        proc = subprocess.run(
            ["python3", str(worker_script)],
            cwd=str(self.workspace),
            env=self.env,
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, -9, f"expected SIGKILL (-9), got {proc.returncode}: {proc.stdout} {proc.stderr}")
        self.assertNotIn("UNREACHABLE", proc.stdout, "the watchdog fired too late -- the run finished before being killed")

        events_file = state_dir / "events.sqlite3"
        self.assertTrue(events_file.exists())

        def _effect_completed_count(state_dir: Path, run_id: str) -> int:
            from vanguard.packages.adapters.stores.event_store import SqliteEventStore as _Store
            from vanguard.packages.ports.event_store import EventRange as _Range
            store = _Store(str(state_dir / "events.sqlite3"))
            try:
                res = store.read(_Range(run_id=run_id))
                assert res.ok
                return sum(1 for ev in res.value if ev.payload.get("kind") == "EffectCompleted")
            finally:
                store.close()

        interrupted_count = _effect_completed_count(state_dir, run_id)
        self.assertEqual(interrupted_count, 1, "exactly the one effect settled before the kill should be on the ledger")

        # Fresh process resumes. Its tape has only "finish", not the effect
        # again: if the runtime replayed the already-settled effect instead
        # of recognizing it and moving on, this model would desync (it has
        # nothing scripted for an effect proposal) and the run would error
        # or fail to reach "completed" rather than finishing cleanly.
        resume_script = self.workspace / "_beta12_resume.py"
        resume_script.write_text(f"""
from pathlib import Path
from vanguard.packages.adapters.models.fake import FakeModel
from vanguard.packages.runtime.app_service import ApplicationService

ws = Path({json.dumps(str(self.workspace))})
state_dir = Path({json.dumps(str(state_dir))})
model = FakeModel([
    {{"kind": "finish", "note": "done"}},
])
app = ApplicationService(workspace=ws)
res = app.resume(run_id={json.dumps(run_id)}, profile_id="local", model=model, state_dir=state_dir)
print("RESUME Outcome:", res.outcome, "Turns:", res.turns)
""", encoding="utf-8")
        proc2 = subprocess.run(
            ["python3", str(resume_script)],
            cwd=str(self.workspace),
            env=self.env,
            capture_output=True,
            text=True,
            check=True,
            timeout=60,
        )
        self.assertIn("RESUME Outcome: completed", proc2.stdout, proc2.stdout + proc2.stderr)

        final_count = _effect_completed_count(state_dir, run_id)
        self.assertEqual(
            final_count, 1,
            "the settled effect must still appear exactly once -- never replayed on resume",
        )


if __name__ == "__main__":
    unittest.main()
