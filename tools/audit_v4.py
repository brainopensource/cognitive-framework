#!/usr/bin/env python3
"""tools/audit_v4.py — reference and namespace audit for the v4 document set.

Implements CI-2 (no pre-v4 references), CI-3 (cross-references resolve),
CI-4 (no identifier defined in two documents), CI-7 (declared namespaces).

Exit code 1 on any BROKEN finding. PENDING findings (targets not yet authored)
are reported and do not fail, so the audit is usable mid-authoring.
"""
import re, sys, glob, os
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


DOCS = sorted(glob.glob("[0-9][0-9]_vanguard_*.md"))
REGISTRY = "00_vanguard_registry_v040.md"

PRE_V4 = [
    "vanguard_architecture_and_core_specification_v2", "vanguard_02_loop_engineering",
    "vanguard_03_core_contracts_and_trajectory_schema", "vanguard_04_kernel_and_security",
    "vanguard_05_phase_0_build_plan", "vanguard_00_engineering_handbook",
    "vanguard_achf_substrate_adequacy_review", "Parecer_Arquitetural",
    "Especificacao_Base", "Guia_Navegacao", "REG-D_Consolidation",
]

def index(path):
    """Return the set of section numbers a document defines, e.g. {'0','1','5.2'}."""
    secs = set()
    for line in open(path):
        m = re.match(r"^#{2,3}\s+(?:§\s*)?(\d+(?:\.\d+)*)[.\s]", line)
        if m:
            secs.add(m.group(1))
            secs.add(m.group(1).split(".")[0])
    return secs

def main():
    present = {d[:2]: d for d in DOCS}
    sections = {k: index(v) for k, v in present.items()}
    findings = defaultdict(list)

    # --- declared namespaces (CI-7) -------------------------------------
    declared = {}
    if os.path.exists(REGISTRY):
        for line in open(REGISTRY):
            m = re.match(r"\|\s*`([A-Z]{1,4})-?[a-zA-Z0-9]*`(?:[^|]*)\|([^|]*)\|\s*([^|]*)\|", line)
            if m and m.group(3).strip():
                owners = re.findall(r"\b(\d\d)\b", m.group(3))
                if "schemas" in m.group(3):
                    owners = ["--"]          # owned outside the document set
                if owners:
                    declared[m.group(1)] = set(owners)

    # --- scan every document --------------------------------------------
    defined_by = defaultdict(set)
    for num, path in present.items():
        body = open(path).read()

        # CI-2: pre-v4 references (registry ch.7 is the allow-listed exception)
        if num != "00":
            for token in PRE_V4:
                if token in body:
                    findings["BROKEN"].append(f"{path}: references pre-v4 source '{token}' (CI-2)")

        # CI-3: cross-document references of the form `NN §M`
        for ref_doc, ref_sec in re.findall(r"`(\d\d)\s+§(\d+(?:\.\d+)*)", body):
            if ref_doc == num:
                continue
            if ref_doc not in present:
                findings["PENDING"].append(f"{path}: -> {ref_doc} §{ref_sec} (target not yet authored)")
            elif ref_sec not in sections[ref_doc] and ref_sec.split(".")[0] not in sections[ref_doc]:
                findings["BROKEN"].append(f"{path}: -> {ref_doc} §{ref_sec} does not exist (CI-3)")

        # bare document references
        for ref_doc in re.findall(r"`(\d\d)`", body):
            if ref_doc not in present and ref_doc != num:
                findings["PENDING"].append(f"{path}: -> {ref_doc} (target not yet authored)")

        # CI-4 / CI-7: identifier DEFINITIONS only — first table cell or a
        # blockquote definition. An ID in any other cell is a reference, and
        # counting references as definitions produced false CI-7 failures.
        for pid in rule_defs(path):
            prefix = pid[0]
            defined_by[prefix].add(num)
            if prefix in declared and num not in declared[prefix] and num != "00":
                findings["BROKEN"].append(
                    f"{path}: defines `{prefix}-` but registry assigns it to {sorted(declared[prefix])} (CI-7)")
            if prefix not in declared and num != "00":
                findings["BROKEN"].append(f"{path}: `{prefix}-` is not declared in the registry namespace table (CI-7)")

    for prefix, docs in defined_by.items():
        owners = {d for d in docs if d != "00"}
        if len(owners) > 1:
            findings["BROKEN"].append(f"`{prefix}-` defined in multiple documents {sorted(owners)} (CI-4)")

    for level in ("BROKEN", "PENDING"):
        seen = set()
        for f in findings[level]:
            if f not in seen:
                seen.add(f)
                print(f"{level}: {f}")
        if level == "BROKEN" and not findings[level]:
            print("BROKEN: none")

    return 1 if findings["BROKEN"] else 0

if __name__ == "__main__":
    sys.exit(main())
