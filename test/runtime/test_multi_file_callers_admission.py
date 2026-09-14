"""T-83b: a public-symbol edit cannot finish while its callers are unread.

The subject is the pure policy `ADR-0107` assigns to lane B: it consumes
`CallerAdmissionEvidence` and returns a typed verdict. Nothing here touches a
port, an index, or a workspace -- the evidence arrives as values, which is the
point. The runtime session owns collection; this module owns only the rule.

The corpus is drawn from caller topologies that actually occur in this
repository rather than invented ones: `unique_str_replace` is defined in
`environment/hunks.py` and called from two separate adapters, which is exactly
the one-definition / many-callers shape this gate exists for.
"""

from __future__ import annotations

import unittest

from vanguard.packages.agency.multi_file_completeness import (
    CALLER_ADMISSION_OK,
    CALLER_COVERAGE_UNRESOLVED,
    INSPECTION_EVIDENCE_STALE,
    NO_PUBLIC_SYMBOL_CHANGE,
    UNINSPECTED_CALLERS_REMAINING,
    VERIFICATION_NOT_BOUND_TO_CANDIDATE,
    CallerAdmissionEvidence,
    evaluate_caller_admission,
    omit_uninspected_caller,
)
from vanguard.packages.domain.workspace_epoch import WorkspaceEpoch
from vanguard.packages.ports.index import Symbol

TASK = "sha256:task"
COMPOSITION = "sha256:composition"
CANDIDATE = (TASK, COMPOSITION, "sha256:tree-current")
SUPERSEDED = (TASK, COMPOSITION, "sha256:tree-superseded")
TREE = CANDIDATE[2]
OLD_TREE = SUPERSEDED[2]

EPOCH = WorkspaceEpoch(
    tree_hash=TREE,
    index_digest="sha256:index",
    source_revision="cba24fda",
    compiled_at_turn=4,
)


def _sym(path: str, name: str = "public_api") -> Symbol:
    return Symbol(name=name, kind="function", path=path, line=1)


# The named acceptance topology: `file_a.py` defines the public symbol,
# `file_b.py` calls it.
FILE_A = _sym("file_a.py")
FILE_B = _sym("file_b.py", name="caller_of_public_api")
FILE_C = _sym("file_c.py", name="other_caller_of_public_api")


def _evidence(**overrides) -> CallerAdmissionEvidence:
    base = dict(
        changed_public_symbols=(FILE_A,),
        inspected_callers=(FILE_B,),
        updated_callers=(),
        inspection_receipts=((FILE_B, TREE),),
        update_receipts=(),
        omissions=(),
        candidate_identity=CANDIDATE,
        source_identity=EPOCH,
        unresolved_coverage=False,
    )
    base.update(overrides)
    return CallerAdmissionEvidence(**base)


def _admit(evidence: CallerAdmissionEvidence, **overrides):
    kwargs = dict(verification_passed=True, verification_candidate_identity=CANDIDATE)
    kwargs.update(overrides)
    return evaluate_caller_admission(evidence, **kwargs)


class TestUninspectedCallersRemaining(unittest.TestCase):
    """The named acceptance falsifier: file_a.py blocked until file_b.py is seen."""

    def test_uninspected_caller_yields_the_typed_rejection(self) -> None:
        verdict = _admit(_evidence(
            inspected_callers=(),
            inspection_receipts=(),
            omissions=(omit_uninspected_caller(FILE_B),),
        ))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, UNINSPECTED_CALLERS_REMAINING)
        self.assertEqual(verdict.uninspected_callers, ("file_b.py",))
        self.assertIn("file_b.py", verdict.rejection_feedback or "")

    def test_inspecting_the_caller_admits_the_change(self) -> None:
        verdict = _admit(_evidence())
        self.assertTrue(verdict.admissible, verdict.rejection_feedback)
        self.assertEqual(verdict.reason, CALLER_ADMISSION_OK)

    def test_updating_the_caller_also_admits_the_change(self) -> None:
        verdict = _admit(_evidence(
            inspected_callers=(),
            inspection_receipts=(),
            updated_callers=(FILE_B,),
            update_receipts=((FILE_B, TREE),),
        ))
        self.assertTrue(verdict.admissible, verdict.rejection_feedback)
        self.assertEqual(verdict.reason, CALLER_ADMISSION_OK)

    def test_a_claimed_caller_without_a_receipt_is_not_covered(self) -> None:
        verdict = _admit(_evidence(inspection_receipts=()))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, UNINSPECTED_CALLERS_REMAINING)
        self.assertEqual(verdict.uninspected_callers, ("file_b.py",))

    def test_a_change_with_no_public_symbol_is_not_this_policys_subject(self) -> None:
        verdict = _admit(_evidence(changed_public_symbols=()))
        self.assertTrue(verdict.admissible)
        self.assertEqual(verdict.reason, NO_PUBLIC_SYMBOL_CHANGE)

    def test_an_uninspected_caller_does_burn_a_reasoning_retry(self) -> None:
        verdict = _admit(_evidence(
            inspected_callers=(), inspection_receipts=(),
            omissions=(omit_uninspected_caller(FILE_B),)))
        self.assertEqual(verdict.reason, UNINSPECTED_CALLERS_REMAINING)
        self.assertTrue(verdict.consumes_reasoning_retry)


class TestUnresolvedCoverageIsNotAnEmptyGraph(unittest.TestCase):
    """Missing, stale, truncated or unbound coverage may never read as complete."""

    def test_unresolved_coverage_refuses_even_with_every_caller_inspected(self) -> None:
        verdict = _admit(_evidence(unresolved_coverage=True))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, CALLER_COVERAGE_UNRESOLVED)

    def test_unresolved_coverage_does_not_burn_a_reasoning_retry(self) -> None:
        verdict = _admit(_evidence(unresolved_coverage=True))
        self.assertFalse(verdict.consumes_reasoning_retry)

    def test_a_non_caller_omission_is_unresolved_coverage(self) -> None:
        verdict = _admit(_evidence(omissions=("index_query_truncated",)))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, CALLER_COVERAGE_UNRESOLVED)
        self.assertFalse(verdict.consumes_reasoning_retry)
        self.assertIn("index_query_truncated", verdict.omissions)

    def test_a_genuinely_empty_resolved_caller_set_is_admissible(self) -> None:
        verdict = _admit(_evidence(
            inspected_callers=(), inspection_receipts=(), omissions=()))
        self.assertTrue(verdict.admissible, verdict.rejection_feedback)
        self.assertEqual(verdict.reason, CALLER_ADMISSION_OK)

    def test_unresolved_coverage_outranks_an_apparently_complete_surface(self) -> None:
        verdict = _admit(_evidence(
            inspected_callers=(), inspection_receipts=(),
            omissions=(), unresolved_coverage=True))
        self.assertEqual(verdict.reason, CALLER_COVERAGE_UNRESOLVED)


class TestCandidateBoundEvidence(unittest.TestCase):
    """A later edit invalidates the receipts, and the verification it moved."""

    def test_a_receipt_from_an_earlier_candidate_does_not_count(self) -> None:
        verdict = _admit(_evidence(inspection_receipts=((FILE_B, OLD_TREE),)))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, INSPECTION_EVIDENCE_STALE)
        self.assertIn("file_b.py", verdict.stale_receipts)
        self.assertIn("re-read", (verdict.rejection_feedback or "").lower())

    def test_never_read_outranks_invalidated_when_both_are_present(self) -> None:
        verdict = _admit(_evidence(
            inspected_callers=(FILE_B,),
            inspection_receipts=((FILE_B, OLD_TREE),),
            omissions=(omit_uninspected_caller(FILE_C),),
        ))
        self.assertEqual(verdict.reason, UNINSPECTED_CALLERS_REMAINING)
        self.assertEqual(verdict.uninspected_callers, ("file_b.py", "file_c.py"))
        self.assertEqual(verdict.diagnostics["never_inspected"], ("file_c.py",))
        self.assertEqual(verdict.diagnostics["invalidated_by_later_edit"], ("file_b.py",))

    def test_evidence_naming_no_candidate_tree_is_refused(self) -> None:
        verdict = _admit(_evidence(candidate_identity=(TASK, COMPOSITION, "")))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, VERIFICATION_NOT_BOUND_TO_CANDIDATE)
        self.assertEqual(verdict.diagnostics["cause"], "candidate_identity_unbound")

    def test_inspection_alone_is_not_proof_of_behaviour(self) -> None:
        verdict = _admit(_evidence(), verification_passed=False)
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, VERIFICATION_NOT_BOUND_TO_CANDIDATE)

    def test_a_tree_mutated_after_verification_cannot_reuse_the_verdict(self) -> None:
        verdict = _admit(_evidence(), verification_candidate_identity=SUPERSEDED)
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, VERIFICATION_NOT_BOUND_TO_CANDIDATE)
        self.assertEqual(
            verdict.diagnostics["cause"], "post_verification_tree_mutation")

    def test_a_verification_on_a_different_task_is_foreign(self) -> None:
        verdict = _admit(_evidence(), verification_candidate_identity=(
            "sha256:other-task", COMPOSITION, TREE))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, VERIFICATION_NOT_BOUND_TO_CANDIDATE)

    def test_an_unbound_verification_subject_is_refused(self) -> None:
        verdict = _admit(_evidence(), verification_candidate_identity=None)
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, VERIFICATION_NOT_BOUND_TO_CANDIDATE)


class TestRealFiveFileTopology(unittest.TestCase):
    """A five-file change spanning a public helper and its production callers."""

    _SYMBOLS = (
        Symbol(name="unique_str_replace", kind="function",
               path="vanguard/packages/adapters/environment/hunks.py", line=38),
        Symbol(name="AtomicMultiFileTransactionManager.execute_transaction",
               kind="method",
               path="vanguard/packages/adapters/environment/transaction.py", line=51),
    )
    _CALLERS = (
        _sym("vanguard/packages/adapters/environment/fake.py", "FakeEnvironment.apply"),
        _sym("vanguard/packages/adapters/environment/git.py", "GitEnvironment.apply"),
        _sym("vanguard/packages/adapters/environment/sandboxed.py", "SandboxedEnvironment.apply"),
    )

    def _evidence(self, **overrides) -> CallerAdmissionEvidence:
        base = dict(
            changed_public_symbols=self._SYMBOLS,
            inspected_callers=self._CALLERS,
            inspection_receipts=tuple((caller, TREE) for caller in self._CALLERS),
            candidate_identity=CANDIDATE,
            source_identity=EPOCH,
        )
        base.update(overrides)
        return CallerAdmissionEvidence(**base)

    def test_the_full_surface_admits_only_with_every_caller_covered(self) -> None:
        verdict = _admit(self._evidence())
        self.assertTrue(verdict.admissible, verdict.rejection_feedback)
        self.assertEqual(verdict.reason, CALLER_ADMISSION_OK)

    def test_dropping_one_caller_refuses_the_whole_change(self) -> None:
        for omitted in self._CALLERS:
            with self.subTest(omitted=omitted.path):
                kept = tuple(c for c in self._CALLERS if c.path != omitted.path)
                verdict = _admit(self._evidence(
                    inspected_callers=kept,
                    inspection_receipts=tuple((c, TREE) for c in kept),
                    omissions=(omit_uninspected_caller(omitted),),
                ))
                self.assertFalse(verdict.admissible)
                self.assertEqual(verdict.reason, UNINSPECTED_CALLERS_REMAINING)
                self.assertIn(omitted.path, verdict.uninspected_callers)

    def test_one_stale_receipt_of_three_refuses_the_whole_change(self) -> None:
        receipts = ((self._CALLERS[0], OLD_TREE),) + tuple(
            (c, TREE) for c in self._CALLERS[1:])
        verdict = _admit(self._evidence(inspection_receipts=receipts))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, INSPECTION_EVIDENCE_STALE)
        self.assertEqual(verdict.stale_receipts, (self._CALLERS[0].path,))

    def test_unresolved_coverage_refuses_the_whole_change(self) -> None:
        verdict = _admit(self._evidence(unresolved_coverage=True))
        self.assertFalse(verdict.admissible)
        self.assertEqual(verdict.reason, CALLER_COVERAGE_UNRESOLVED)
        self.assertFalse(verdict.consumes_reasoning_retry)


class TestAdrFieldInventory(unittest.TestCase):
    """`ADR-0107` fixes the cross-lane field inventory of B's seam type."""

    def test_caller_admission_evidence_matches_the_binding_decision(self) -> None:
        import dataclasses

        fields = tuple(f.name for f in dataclasses.fields(CallerAdmissionEvidence))
        self.assertEqual(fields, (
            "changed_public_symbols",
            "inspected_callers",
            "updated_callers",
            "inspection_receipts",
            "update_receipts",
            "omissions",
            "candidate_identity",
            "source_identity",
            "unresolved_coverage",
        ))

    def test_the_evidence_and_verdict_are_frozen_values(self) -> None:
        from vanguard.packages.agency.multi_file_completeness import (
            CallerAdmissionVerdict,
        )

        for cls in (CallerAdmissionEvidence, CallerAdmissionVerdict):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(cls.__dataclass_params__.frozen)


class TestPolicyPurity(unittest.TestCase):
    """The policy holds no authority and reaches nothing."""

    def test_module_imports_no_adapter_io_or_port_protocol(self) -> None:
        import ast
        import inspect

        from vanguard.packages.agency import multi_file_completeness as policy

        tree = ast.parse(inspect.getsource(policy))
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
                imported.extend(f"{node.module or ''}.{a.name}" for a in node.names)
        forbidden = ("os", "pathlib", "subprocess", "sqlite3", "ast", "shutil", "socket")
        self.assertEqual(
            [name for name in imported if name.split(".")[0] in forbidden], [])
        self.assertEqual([name for name in imported if "adapters" in name], [])
        # Value types from the index port are the seam; the Protocol is not.
        self.assertNotIn("..ports.index.IndexPort", imported)

    def test_evaluation_is_deterministic_and_mutates_no_input(self) -> None:
        evidence = _evidence()
        first = _admit(evidence)
        second = _admit(evidence)
        self.assertEqual(first, second)
        self.assertEqual(evidence, _evidence())


if __name__ == "__main__":
    unittest.main()
