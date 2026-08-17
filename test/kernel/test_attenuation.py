"""Attenuation algebra (`05 §4`) and grant obligations (`05 §3`).

The attenuation relation must be **strictly monotone-decreasing**: a child can
only ever hold less than its parent. That is an algebraic claim, so it is
tested as one — over a generated population, with a fixed seed so a
counterexample is reproducible (`verification-threat-evaluation-plan.md` §2,
property family).
"""

from __future__ import annotations

import itertools
import random
import unittest

from vanguard.packages.kernel import (
    Constraints,
    FailurePath,
    GrantIssuer,
    HmacAuthenticator,
    MissingDescriptorBinding,
    Scope,
    attenuate,
    descriptor_of,
)
from vanguard.packages.kernel.attenuation import covers, resource_subset

from . import fakes

SEED = 20260815

ACTIONS = ("fs.read", "fs.write", "net.fetch", "exec.run")
RESOURCES = (
    {"kind": "fs", "root": "/workspace", "paths": ["/workspace"]},
    {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src"]},
    {"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/a.ts"]},
    {"kind": "fs", "root": "/etc", "paths": ["/etc"]},
    {"kind": "network", "hosts": ["*.example.com"], "ports": [443]},
    {"kind": "network", "hosts": ["api.example.com"], "ports": [443]},
    {"kind": "generic", "uriPattern": "vg://tool/echo"},
)
EXPIRIES = ("2026-08-15T10:00:00.000Z", "2026-08-15T12:00:00.000Z", "2099-01-01T00:00:00.000Z")
RISKS = ("low", "medium", "high", "critical")


def _population(rng: random.Random, size: int) -> list[Scope]:
    out = []
    for _ in range(size):
        out.append(Scope(
            actions=frozenset(rng.sample(ACTIONS, rng.randint(1, 3))),
            resources=tuple(rng.sample(RESOURCES, rng.randint(1, 3))),
            constraints=Constraints(
                expires_at=rng.choice(EXPIRIES),
                max_uses=rng.choice([1, 4, 16]),
                budget_usd_micros=rng.choice([1_000, 100_000]),
                max_bytes=rng.choice([None, 1024, 1_048_576]),
                risk_ceiling=rng.choice(RISKS),
                max_depth=rng.choice([2, 4, 8]),
                network_policy=rng.choice(["deny", "allowlist"]),
            ),
            depth=rng.randint(0, 2),
        ))
    return out


class MonotoneDecrease(unittest.TestCase):
    """`K-23`: attenuation narrows, and the result is a subset of both."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.population = _population(random.Random(SEED), 60)

    def test_a_granted_child_is_never_wider_than_its_parent(self) -> None:
        for parent, request in itertools.permutations(self.population, 2):
            result = attenuate(parent, request)
            if result.ok:
                with self.subTest(parent=parent, request=request):
                    self.assertTrue(covers(parent, result.granted),
                                    "attenuation produced a child wider than its parent")

    def test_a_granted_child_is_never_wider_than_the_request(self) -> None:
        for parent, request in itertools.permutations(self.population, 2):
            result = attenuate(parent, request)
            if result.ok:
                with self.subTest(parent=parent, request=request):
                    self.assertTrue(covers(request, result.granted))

    def test_attenuation_is_idempotent(self) -> None:
        for parent, request in itertools.permutations(self.population, 2):
            first = attenuate(parent, request)
            if not first.ok:
                continue
            with self.subTest(parent=parent, request=request):
                second = attenuate(parent, first.granted)
                self.assertTrue(second.ok)
                self.assertEqual(second.granted.actions, first.granted.actions)
                self.assertEqual(second.granted.resources, first.granted.resources)
                self.assertEqual(second.granted.constraints, first.granted.constraints)

    def test_every_pair_decides(self) -> None:
        """Total: a pair is granted or denied, never left undecided."""
        for parent, request in itertools.product(self.population, repeat=2):
            result = attenuate(parent, request)
            with self.subTest(parent=parent, request=request):
                # Granted exactly when there is no denial, and vice versa.
                self.assertEqual(result.ok, result.denial is None)


class NoSilentIntersection(unittest.TestCase):
    """`K-25`, `K-26`, `K-27` — and `MF-KRN-004`."""

    def test_an_over_broad_request_is_denied_whole(self) -> None:
        parent = fakes.parent_scope()
        request = fakes.child_scope(resources=(fakes.WORKSPACE, fakes.ETC))
        result = attenuate(parent, request)
        self.assertFalse(result.ok)
        # Not "granted with /etc removed" — denied, with both sides recorded.
        self.assertIsNone(result.granted)

    def test_the_denial_records_requested_and_grantable(self) -> None:
        """`K-25`: a denial that does not say what was grantable is not
        actionable, and the escalation signal is lost."""
        parent = fakes.parent_scope()
        request = fakes.child_scope(resources=(fakes.WORKSPACE, fakes.ETC))
        denial = attenuate(parent, request).denial
        self.assertEqual(denial.dimension, "resources")
        self.assertIn(fakes.ETC, denial.requested)
        self.assertIn(fakes.WORKSPACE, denial.grantable)
        self.assertTrue(denial.alertable)

    def test_scope_escalation_is_alertable_through_dispatch(self) -> None:
        """`K-27`, `F-10`: an alertable event, never a log line."""
        harness = fakes.build()
        result = harness.kernel.dispatch(
            fakes.request(), requested_scope=fakes.child_scope(resources=(fakes.ETC,)),
            reservation=fakes.reservation())
        self.assertIs(result.failure, FailurePath.DENIED_SCOPE_ESCALATION)
        denial = result.events[-1]
        self.assertTrue(denial.alertable)
        self.assertIn("requested", denial.payload)
        self.assertIn("grantable", denial.payload)

    def test_extra_actions_deny(self) -> None:
        denial = attenuate(fakes.parent_scope(),
                           fakes.child_scope(actions=frozenset({"exec.run"}))).denial
        self.assertEqual(denial.dimension, "actions")

    def test_undefined_selector_pairs_are_denied(self) -> None:
        """`K-48`: total on defined pairs, denying everything else."""
        parent = fakes.parent_scope()
        for resource in (
            {"kind": "generic", "uriPattern": "file:///workspace/src"},
            {"kind": "network", "hosts": ["example.com"], "ports": [443]},
            {"kind": "process", "pid": 1},
        ):
            with self.subTest(resource=resource):
                self.assertFalse(attenuate(parent, fakes.child_scope(
                    resources=(resource,))).ok)

    def test_resource_subset_helper_agrees_with_the_domain_relation(self) -> None:
        self.assertTrue(resource_subset(
            [fakes.WORKSPACE],
            [{"kind": "fs", "root": "/workspace", "paths": ["/workspace/src/deep/a.ts"]}]))
        self.assertFalse(resource_subset([fakes.WORKSPACE], [fakes.ETC]))


class ConstraintCeilings(unittest.TestCase):
    """No constraint may increase: time, uses, bytes, budget, risk, surface."""

    def test_each_dimension_denies_when_it_widens(self) -> None:
        parent = fakes.parent_scope()
        cases = {
            "constraints.expiresAt": {"expires_at": "2099-06-06T00:00:00.000Z"},
            "constraints.maxUses": {"max_uses": 99},
            "constraints.budget": {"budget_usd_micros": 9_999_999},
            "constraints.maxBytes": {"max_bytes": 99_999_999},
            "constraints.requireApprovalAboveRisk": {"risk_ceiling": "critical"},
            "constraints.depth": {"max_depth": 99},
            "constraints.networkPolicy": {"network_policy": "allowlist"},
        }
        for dimension, override in cases.items():
            with self.subTest(dimension=dimension):
                request = fakes.child_scope(constraints=fakes.constraints(**override))
                result = attenuate(parent, request)
                self.assertFalse(result.ok, f"{dimension} widened without denial")
                self.assertEqual(result.denial.dimension, dimension)

    def test_lowering_every_dimension_is_allowed(self) -> None:
        request = fakes.child_scope(constraints=fakes.constraints(
            expires_at="2026-08-15T09:30:00.000Z", max_uses=1,
            budget_usd_micros=10, max_bytes=64, risk_ceiling="low",
            max_depth=1, network_policy="deny"))
        self.assertTrue(attenuate(fakes.parent_scope(), request).ok)

    def test_depth_is_parent_plus_one_and_bounded(self) -> None:
        """`K-24`."""
        parent = fakes.parent_scope()
        granted = attenuate(parent, fakes.child_scope()).granted
        self.assertEqual(granted.depth, parent.depth + 1)
        deep = Scope(actions=parent.actions, resources=parent.resources,
                     constraints=fakes.constraints(), depth=parent.constraints.max_depth)
        self.assertFalse(attenuate(deep, fakes.child_scope()).ok)

    def test_a_child_is_sealed_when_the_parent_withholds_verbs(self) -> None:
        """`ADR-0067`: withheld verbs mark the grant sealed; equal verbs do not."""
        parent = fakes.parent_scope()
        narrowed = attenuate(parent, fakes.child_scope()).granted
        self.assertTrue(narrowed.sealed)
        same = attenuate(parent, fakes.child_scope(actions=parent.actions,
                                                  resources=parent.resources)).granted
        self.assertFalse(same.sealed)


class GrantObligations(unittest.TestCase):
    """`K-18`..`K-21`, `K-49` — and `MF-KRN-003`, `MF-KRN-005`."""

    def setUp(self) -> None:
        self.issuer = GrantIssuer(HmacAuthenticator(b"kernel-test-key"))
        self.descriptor = descriptor_of("fs.write", {"path": "/workspace/src/a.ts"})
        self.scope = fakes.child_scope()

    def _issue(self, **overrides):
        kwargs = {
            "grant_id": "grant-1", "principal": "agent-1",
            "descriptor_digest": self.descriptor, "scope": self.scope,
            "expires_at": "2026-08-15T10:00:00.000Z",
            "purpose_digest": "sha256:" + "a" * 64,
        }
        kwargs.update(overrides)
        return self.issuer.issue(**kwargs)

    def test_a_grant_without_a_descriptor_binding_cannot_be_issued(self) -> None:
        """`K-18` / `CT-51`, and `MF-KRN-003`: without this field the
        point-of-effect check has nothing to compare."""
        with self.assertRaises(MissingDescriptorBinding):
            self._issue(descriptor_digest="")

    def test_purpose_is_not_the_descriptor(self) -> None:
        """`CT-51`: purpose is the brief the effect serves, descriptor is the
        exact call. They are different fields, and both are required."""
        with self.assertRaises(MissingDescriptorBinding):
            self._issue(purpose_digest="")

    def test_descriptor_substitution_is_rejected_at_the_point_of_effect(self) -> None:
        """Approve descriptor A, mutate the arguments to B (`F-14`)."""
        grant = self._issue()
        mutated = descriptor_of("fs.write", {"path": "/etc/shadow"})
        verification = self.issuer.verify(grant, descriptor_digest=mutated,
                                          now="2026-08-15T09:00:00.000Z")
        self.assertFalse(verification.ok)
        self.assertIs(verification.failure, FailurePath.GRANT_MISMATCH)

    def test_the_provider_call_id_is_excluded_from_the_descriptor(self) -> None:
        """`D-3`: it differs between otherwise identical calls."""
        self.assertEqual(
            descriptor_of("fs.write", {"path": "/a", "toolCallId": "call_1"}),
            descriptor_of("fs.write", {"path": "/a", "toolCallId": "call_2"}))

    def test_absent_and_null_arguments_agree(self) -> None:
        """`D-5`: presence with a null value must not differ from absence."""
        self.assertEqual(descriptor_of("fs.write", {"path": "/a", "mode": None}),
                         descriptor_of("fs.write", {"path": "/a"}))

    def test_expired_grant_is_rejected(self) -> None:
        """`F-15`, with an injected clock rather than a sleep."""
        grant = self._issue()
        verification = self.issuer.verify(grant, descriptor_digest=self.descriptor,
                                          now="2026-08-15T11:00:00.000Z")
        self.assertIs(verification.failure, FailurePath.GRANT_EXPIRED)

    def test_replayed_single_use_grant_is_rejected(self) -> None:
        """`F-16`, `K-19`."""
        grant = self._issue()
        now = "2026-08-15T09:00:00.000Z"
        self.assertTrue(self.issuer.verify(grant, descriptor_digest=self.descriptor,
                                           now=now).ok)
        self.issuer.consume(grant)
        second = self.issuer.verify(grant, descriptor_digest=self.descriptor, now=now)
        self.assertIs(second.failure, FailurePath.GRANT_REPLAY)

    def test_forged_authenticator_is_rejected_and_alertable(self) -> None:
        """`F-17`, `K-20`."""
        from dataclasses import replace

        grant = self._issue(cross_process=True)
        self.assertIsNotNone(grant.authenticator)
        forged = replace(grant, authenticator="0" * 64)
        verification = self.issuer.verify(forged, descriptor_digest=self.descriptor,
                                          now="2026-08-15T09:00:00.000Z",
                                          cross_process=True)
        self.assertIs(verification.failure, FailurePath.GRANT_FORGED)

    def test_authenticator_covers_the_whole_grant(self) -> None:
        """A mutated scope invalidates the MAC, not only a mutated digest."""
        from dataclasses import replace

        grant = self._issue(cross_process=True)
        widened = replace(grant, scope=fakes.child_scope(
            actions=frozenset({"fs.write", "exec.run"})))
        self.assertIs(
            self.issuer.verify(widened, descriptor_digest=self.descriptor,
                               now="2026-08-15T09:00:00.000Z", cross_process=True).failure,
            FailurePath.GRANT_FORGED)

    def test_revocation_is_transitive_over_descendants(self) -> None:
        """`K-49`: immediate, transitive, and it emits."""
        self._issue(grant_id="root")
        self._issue(grant_id="child", parent_grant_id="root")
        self._issue(grant_id="grandchild", parent_grant_id="child")
        revoked = self.issuer.revoke("root")
        self.assertEqual(set(revoked), {"root", "child", "grandchild"})
        for grant_id in revoked:
            self.assertTrue(self.issuer.is_revoked(grant_id))

    def test_a_revoked_grant_stops_verifying(self) -> None:
        grant = self._issue()
        self.issuer.revoke("grant-1")
        self.assertFalse(self.issuer.verify(grant, descriptor_digest=self.descriptor,
                                            now="2026-08-15T09:00:00.000Z").ok)

    def test_no_universal_fixed_ttl(self) -> None:
        """`K-21`: a thirty-second default silently breaks every legitimate
        long operation. Expiry comes from the grant's own constraints."""
        long_running = self._issue(grant_id="long", expires_at="2099-01-01T00:00:00.000Z")
        self.assertTrue(self.issuer.verify(long_running, descriptor_digest=self.descriptor,
                                           now="2030-01-01T00:00:00.000Z").ok)
