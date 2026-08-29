"""Import all 29 real SWE-bench Verified challenges from challenges.py into lam.sqlite and scenarios/."""

import json
import sqlite3
import hashlib
from pathlib import Path
import sys

LAM_DIR = Path(__file__).resolve().parent
DB_PATH = LAM_DIR / "lam.sqlite"
SCENARIOS_DIR = LAM_DIR / "scenarios"
ROOT = LAM_DIR.parent.parent

if str(LAM_DIR) not in sys.path:
    sys.path.insert(0, str(LAM_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema import validate_scenario
from store import LamStore
from benchmarks.swe_bench.challenges import CHALLENGES

def import_all_swe_challenges():
    store = LamStore(DB_PATH)
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    
    imported_count = 0
    print(f"Importing {len(CHALLENGES)} challenges from challenges.py...")
    
    for cid, chal in CHALLENGES.items():
        scenario_id = f"t{chal.tier}-{cid.replace('_', '-')}"
        scenario_file = SCENARIOS_DIR / f"{scenario_id}.json"
        
        # Build workspace representation
        workspace = dict(chal.files)
        workspace["oracle_test.py"] = chal.oracle_code
        
        atoms = ["view_file", "edit_file", "run_command"]
        turns = [
            {
                "tool_messages_seen": 0,
                "finish_reason": "tool_calls",
                "tool_calls": [
                    {
                        "type": "function",
                        "function": {
                            "name": "view_file",
                            "arguments": json.dumps({"path": list(chal.files.keys())[0]}, sort_keys=True)
                        }
                    }
                ]
            },
            {
                "tool_messages_seen": 1,
                "finish_reason": "stop",
                "tool_calls": [],
                "content": f"Verified SWE challenge solution for {chal.title} ({cid})."
            }
        ]
        
        scenario_data = {
            "id": scenario_id,
            "tier": chal.tier,
            "title": f"SWE-bench: {chal.title}",
            "workspace": workspace,
            "atoms_used": atoms,
            "turns": turns,
            "created_from": f"benchmarks/swe_bench/challenges.py::{cid}"
        }
        
        # Validate schema
        validate_scenario(scenario_data)
        
        # Save JSON scenario file
        scenario_file.write_text(json.dumps(scenario_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        
        # Register in SQLite database
        store.upsert_scenario(
            scenario_id=scenario_id,
            tier=chal.tier,
            title=f"SWE-bench: {chal.title}",
            atoms=atoms,
            n_files=len(workspace),
            n_turns=len(turns),
            created_from=f"benchmarks/swe_bench/challenges.py::{cid}",
            content_hash=hashlib.sha256(json.dumps(scenario_data, sort_keys=True).encode()).hexdigest()
        )
        imported_count += 1
        print(f"  ✅ Imported {scenario_id} (Tier {chal.tier}): {chal.title}")

    print(f"\n🎉 Successfully imported {imported_count} SWE-bench challenges into lam.sqlite!")
    
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM scenarios")
        total_scenarios = cur.fetchone()[0]
        cur.execute("SELECT count(DISTINCT id) FROM scenarios")
        distinct_scenarios = cur.fetchone()[0]
        print(f"📊 Total Scenarios in lam.sqlite: {total_scenarios} (Distinct: {distinct_scenarios})")

if __name__ == "__main__":
    import_all_swe_challenges()
