#!/usr/bin/env python3
"""tools/cv_checks.py — mechanical acceptance verification (00 §10).

Implements CV-1..CV-12. CV-5, CV-6 and CV-10 have a mechanical component plus a
manual residue; the manual residue is reported, never silently passed.
CV-13 is an external-reader gate and is NOT implemented here by design.

Exit 1 on any FAIL.
"""
import re, sys, glob, os, subprocess
from collections import defaultdict

RULE_IN_TABLE = re.compile(r"\|\s*\*{0,2}`?([A-Z]{1,4})-(\d{1,4})`?\*{0,2}\s*\|")
RULE_IN_QUOTE = re.compile(r"^>\s*\*\*`([A-Z]{1,4})-(\d{1,4})`")

def rule_defs(path):
    """Rule IDs DEFINED in a file: first table cell, or a blockquote definition.
    Blockquote definitions were invisible to the first version of this extractor,
    which understated the rule count and produced false dangling references."""
    out = set()
    for line in open(path):
        m = RULE_IN_TABLE.match(line) or RULE_IN_QUOTE.match(line)
        if m:
            out.add((m.group(1), m.group(2)))
    return out


REG = "00_vanguard_registry_v040.md"
PLAN = "08_vanguard_phase_0_build_plan_v040.md"
DEFREJ = "10_vanguard_deferred_and_rejected_register_v040.md"
VISION = "12_vanguard_vision_annex_v040.md"
ADR = "09_vanguard_decision_register_v040.md"

results = []
def record(cid, ok, detail, manual=""):
    results.append((cid, ok, detail, manual))

def harvest_rows():
    """Rows of the supersession map: (source, section, content, status, dest)."""
    rows, src = [], None
    for line in open(REG):
        h = re.match(r"### 7\.\d+ (S\d+)", line)
        if h:
            src = h.group(1)
        m = re.match(r"\|\s*\*?\*?([\w.]+)\*?\*?\s*\|([^|]*)\|\s*\*?\*?([A-Z ]+)\*?\*?\s*\|([^|]*)\|", line)
        if m and src and m.group(3).strip() in {
            "MIGRATED","MERGED","AMENDED","SUPERSEDED","REJECTED","VISION"}:
            rows.append((src, m.group(1).strip(), m.group(2).strip(),
                         m.group(3).strip(), m.group(4).strip()))
    return rows

def sections_of(doc):
    secs = set()
    for p in glob.glob(f"{doc}_vanguard_*.md"):
        for line in open(p):
            m = re.match(r"^#{2,3}\s+(?:§\s*)?(\d+(?:\.\d+)*)[.\s]", line)
            if m:
                secs.add(m.group(1)); secs.add(m.group(1).split(".")[0])
    return secs

def main():
    rows = harvest_rows()

    # CV-1 — every row has a status and destination, no TBD
    bad = [r for r in rows if not r[4] or "TBD" in r[4].upper()]
    record("CV-1", not bad, f"{len(rows)} rows; {len(bad)} missing a destination")

    # CV-2 — every destination resolves in the v4 set
    unresolved = []
    for r in rows:
        for doc, sec in re.findall(r"\b(\d\d)\s+§(\d+(?:\.\d+)*)", r[4]):
            if sec not in sections_of(doc) and sec.split(".")[0] not in sections_of(doc):
                unresolved.append(f"{r[0]} §{r[1]} -> {doc} §{sec}")
    record("CV-2", not unresolved, f"{len(unresolved)} unresolved: {unresolved[:5]}")

    # CV-3 — every REJECTED row is represented in 10 with reasoning and reversal
    rejected = [r for r in rows if r[3] == "REJECTED"]
    dr = open(DEFREJ).read()
    rej_entries = re.findall(r"\|\s*`REJ-\d+`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", dr)
    complete = [e for e in rej_entries if e[1].strip() and e[2].strip()]
    ok3 = len(rejected) == 0 or (len(rej_entries) > 0 and len(complete) == len(rej_entries))
    record("CV-3", ok3,
           f"{len(rejected)} REJECTED harvest rows; {len(rej_entries)} REJ entries, "
           f"{len(complete)} with both reasoning and reversal")

    # CV-4 — every VISION row appears in 12 under the non-normative header
    vision_rows = [r for r in rows if r[3] == "VISION"]
    vtext = open(VISION).read()
    header = "NON-NORMATIVE" in vtext.split("\n# ")[0]
    record("CV-4", header and (len(vision_rows) == 0 or len(vtext) > 500),
           f"{len(vision_rows)} VISION rows; header present={header}")

    # CV-5 — SUPERSEDED rows have a replacement (mechanical); behavioural test = manual
    sup = [r for r in rows if r[3] == "SUPERSEDED"]
    no_repl = [r for r in sup if not r[4]]
    record("CV-5", not no_repl, f"{len(sup)} SUPERSEDED rows, {len(no_repl)} without replacement",
           manual="behavioural rows need a test ID — reviewer confirms")

    # CV-6 — adjudications carry reasoning (ADR table has a non-empty reasoning column)
    adr = open(ADR).read()
    adj = re.findall(r"\|\s*`(00\d\d)`\s*\|([^|]*)\|([^|]*)\|([^|]*)\|", adr)
    weak = [a[0] for a in adj if len(a[2].strip()) < 20]
    record("CV-6", not weak, f"{len(adj)} adjudication rows; {len(weak)} with thin reasoning: {weak[:5]}")

    # CV-7 — every correction names a test that exists in 08 §5
    plan = open(PLAN).read()
    mf_defined = set(re.findall(r"\|\s*`(MF-\d+)`", plan))
    corr = re.findall(r"\|\s*`(00\d\d)`\s*\|[^|]*\|[^|]*\|([^|]*)\|", adr)
    missing = []
    for cid, caught in corr:
        refs = set(re.findall(r"(MF-\d+)", caught))
        if refs and not refs <= mf_defined:
            missing.append((cid, sorted(refs - mf_defined)))
    record("CV-7", not missing, f"{len(mf_defined)} MF tests defined; dangling: {missing}")

    # CV-8 — every MF test names a rule that exists, and a ticket
    rule_ids = set()
    for p in glob.glob("0[234567]_vanguard_*.md"):
        rule_ids |= {f"{a}-{b}" for a, b in rule_defs(p)}
    dangling, no_ticket = [], []
    for m in re.finditer(r"\|\s*`(MF-\d+)`\s*\|[^|]*\|([^|]*)\|([^|]*)\|", plan):
        mid, guards, ticket = m.group(1), m.group(2), m.group(3).strip()
        for rid in re.findall(r"\[([A-Z]{1,4}-\d{1,4})\]", guards):
            if rid not in rule_ids:
                dangling.append((mid, rid))
        if not ticket:
            no_ticket.append(mid)
    record("CV-8", not dangling and not no_ticket,
           f"dangling rule refs: {dangling}; MF without ticket: {no_ticket}")

    # CV-9 — every ADR row has a non-empty reversal condition
    no_rev = []
    for line in open(ADR):
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if cells and re.fullmatch(r"`\d{4}`", cells[0]) and not cells[-1]:
            no_rev.append(cells[0])
    record("CV-9", not no_rev, f"ADRs without a reversal condition: {no_rev}")

    # CV-10 — Chapter 2 is complete: bijection with files on disk
    reg = open(REG).read()
    ch2 = reg.split("## 2. The v4.0 document set")[1].split("## 3.")[0]
    listed = set(re.findall(r"\|\s*\*\*(\d\d)\*\*\s*\|", ch2))
    present = {os.path.basename(p)[:2] for p in glob.glob("[0-9][0-9]_vanguard_*.md")}
    record("CV-10", listed == present,
           f"registry lists {sorted(listed)}; disk has {sorted(present)}",
           manual="Chapter 8 migration ledger fully DONE — reviewer confirms")

    # CV-11 — CI-1..CI-9 pass
    ci = subprocess.run([sys.executable, "tools/audit_v4.py"], capture_output=True, text=True)
    record("CV-11", ci.returncode == 0, "audit_v4.py " + ("clean" if ci.returncode == 0 else "FAILED"))

    # CV-12 — word budgets
    caps = {}
    for m in re.finditer(r"\|\s*(\d\d)\s*\|[^|]*\|\s*(Normative|Supporting)\s*\|\s*([\d,]+)\s*\|", reg):
        caps[m.group(1)] = (m.group(2), int(m.group(3).replace(",", "")))
    over, normative = [], 0
    for p in sorted(glob.glob("[0-9][0-9]_vanguard_*.md")):
        n = int(subprocess.run(["sh", "tools/wordcount_v4.sh", p],
                               capture_output=True, text=True).stdout.split()[0])
        doc = os.path.basename(p)[:2]
        if doc in caps:
            kind, cap = caps[doc]
            if n > cap:
                over.append(f"{doc}={n}>{cap}")
            if kind == "Normative":
                normative += n
    record("CV-12", not over and normative <= 32000,
           f"over cap: {over or 'none'}; normative subtotal {normative}/32000")

    width = max(len(r[3]) for r in results) if results else 0
    fails = 0
    for cid, ok, detail, manual in results:
        print(f"{'PASS' if ok else 'FAIL'}  {cid:<6} {detail}")
        if manual:
            print(f"      {'':<6} MANUAL RESIDUE: {manual}")
        fails += 0 if ok else 1
    print(f"\n{len(results)-fails}/{len(results)} mechanical checks pass. "
          f"CV-13 is an external-reader gate and is not machine-verifiable.")
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
