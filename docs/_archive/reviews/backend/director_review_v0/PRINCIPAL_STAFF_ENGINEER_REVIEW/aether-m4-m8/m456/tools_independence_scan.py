"""Scan real pack manifests and report the M-7 independent fraction."""
import json, sys, glob, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aether_m456.runtime.independence import EffectRef, analyse

def load(root):
    effects=[]
    for f in glob.glob(os.path.join(root,"**","*.json"), recursive=True):
        try: m=json.load(open(f))
        except Exception: continue
        for c in (m.get("capabilities") or []):
            if "verb" in c:
                effects.append(EffectRef(c["verb"], c.get("sink","observation"),
                                         c.get("selector") or {"kind":"unknown"}))
    return effects

for root in sys.argv[1:]:
    e = load(root)
    print(f"\n### {root}  ({len(e)} declared capabilities)")
    for x in e: print(f"   {x.verb:<14} {x.sink:<12} {x.selector.get('kind')}")
    print(analyse(e).summary())
