"""B-O7-01: the hermetic memory double may never be weaker than the engine.

``InMemoryMemoryPort`` carried a fail-open disjunct::

    access.permitted() or (access.grant_ref and access.tenant
                           and access.project and not access.revoked)

The right-hand branch skipped issuer, subject, actions, expiry and the
verification receipt, so a ``MemoryAccess`` that merely *named* a grant could
read and write memory. Nothing caught it, because the double decided
authorization for itself while the durable ``DurableMemoryPort`` decided it properly:
the two implementations were never compared.

This module compares them. For a matrix of access objects spanning every way a
lease can be invalid, the double and the engine must reach the same decision.
A relaxation in either one fails here, whichever side drifts.
"""

from __future__ import annotations

import hashlib
import hmac
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from vanguard.packages.adapters.stores.memory_engine import DurableMemoryPort
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.ports.memory import MemoryAccess, MemoryAuthorizationPort
from vanguard.packages.runtime.memory import InMemoryMemoryPort

_KEY = b"m8-memory-parity-key"
_SELECTOR = {"kind": "project"}


def _now() -> datetime:
    return datetime(2026, 8, 27, 12, 0, 0, tzinfo=timezone.utc)


def _valid_access(actions: tuple[str, ...] = ("read", "write", "invalidate")) -> MemoryAccess:
    grant = {
        "grantRef": "grant-parity",
        "issuer": "runtime",
        "subject": "agent",
        "tenant": "tenant-a",
        "project": "project-a",
        "actions": list(actions),
        "purpose": "parity",
        "expiresAt": (_now() + timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        "revocationEpoch": 1,
        "selector": _SELECTOR,
    }
    signature = hmac.new(_KEY, digest_of(grant).encode("ascii"), hashlib.sha256).hexdigest()
    return MemoryAuthorizationPort(_KEY).verify(
        grant, signature, action="read", tenant="tenant-a", project="project-a",
        selector=_SELECTOR, now=_now(),
    )


def _named_but_unverified() -> MemoryAccess:
    """The exact shape the removed disjunct admitted: a grant in name only."""
    return MemoryAccess("grant-parity", _SELECTOR, "tenant-a", "project-a")


def _cases() -> list[tuple[str, MemoryAccess]]:
    valid = _valid_access()
    return [
        ("named-but-never-verified", _named_but_unverified()),
        ("no-verification-receipt", MemoryAccess(
            grant_ref="grant-parity", selector=_SELECTOR, tenant="tenant-a",
            project="project-a", issuer="runtime", subject="agent",
            actions=("read", "write"), purpose="p",
            expires_at="2099-01-01T00:00:00Z", verification_receipt="")),
        ("revoked", MemoryAccess(
            grant_ref=valid.grant_ref, selector=dict(valid.selector), tenant=valid.tenant,
            project=valid.project, revoked=True, issuer=valid.issuer, subject=valid.subject,
            actions=valid.actions, purpose=valid.purpose, expires_at=valid.expires_at,
            revocation_epoch=valid.revocation_epoch,
            verification_receipt=valid.verification_receipt)),
        ("expired", MemoryAccess(
            grant_ref=valid.grant_ref, selector=dict(valid.selector), tenant=valid.tenant,
            project=valid.project, issuer=valid.issuer, subject=valid.subject,
            actions=valid.actions, purpose=valid.purpose,
            expires_at="2020-01-01T00:00:00Z", revocation_epoch=valid.revocation_epoch,
            verification_receipt=valid.verification_receipt)),
        ("no-actions", MemoryAccess(
            grant_ref=valid.grant_ref, selector=dict(valid.selector), tenant=valid.tenant,
            project=valid.project, issuer=valid.issuer, subject=valid.subject,
            actions=(), purpose=valid.purpose, expires_at=valid.expires_at,
            revocation_epoch=valid.revocation_epoch,
            verification_receipt=valid.verification_receipt)),
        ("no-issuer", MemoryAccess(
            grant_ref=valid.grant_ref, selector=dict(valid.selector), tenant=valid.tenant,
            project=valid.project, issuer="", subject=valid.subject,
            actions=valid.actions, purpose=valid.purpose, expires_at=valid.expires_at,
            revocation_epoch=valid.revocation_epoch,
            verification_receipt=valid.verification_receipt)),
        ("write-action-not-granted", _valid_access(actions=("read",))),
        ("fully-authorized", valid),
    ]


class MemoryDoubleMatchesEngine(unittest.TestCase):
    """The double and the durable engine agree on every authorization decision."""

    def _decisions(self, access: MemoryAccess, action: str) -> tuple[bool, bool]:
        fake = InMemoryMemoryPort("knowledge")
        with tempfile.TemporaryDirectory() as tmp:
            engine = DurableMemoryPort(Path(tmp), "knowledge")

            def attempt(port) -> bool:
                try:
                    if action == "write":
                        port.write({"text": "a fact"}, access)
                    else:
                        port.recall("fact", access)
                except PermissionError:
                    return False
                return True

            return attempt(fake), attempt(engine)

    def test_double_and_engine_agree_on_every_lease(self) -> None:
        for action in ("write", "read"):
            for name, access in _cases():
                with self.subTest(action=action, case=name):
                    fake_ok, engine_ok = self._decisions(access, action)
                    self.assertEqual(
                        fake_ok,
                        engine_ok,
                        f"{name}/{action}: the double says "
                        f"{'allow' if fake_ok else 'deny'} but the engine says "
                        f"{'allow' if engine_ok else 'deny'}. A test double must "
                        f"never be more permissive than what it doubles.",
                    )

    def test_a_grant_in_name_only_is_refused(self) -> None:
        """The removed disjunct, stated directly."""
        access = _named_but_unverified()
        self.assertFalse(access.permitted())
        port = InMemoryMemoryPort("knowledge")
        with self.assertRaises(PermissionError):
            port.write({"text": "a fact"}, access)
        with self.assertRaises(PermissionError):
            port.recall("fact", access)
        with self.assertRaises(PermissionError):
            port.invalidate("knowledge:00000001", access)

    def test_a_fully_authorized_lease_still_works(self) -> None:
        """Fail-closed, not closed to everything."""
        access = _valid_access()
        port = InMemoryMemoryPort("knowledge")
        record_id = port.write({"text": "a durable fact"}, access)
        self.assertEqual(port.recall("durable", access).record_ids, (record_id,))


class AuthorizationPrecedesRankingAndDereference(unittest.TestCase):
    """ADR-0100 ordering: authorize, then rank, then dereference content."""

    def test_unauthorized_recall_never_reaches_the_ranker(self) -> None:
        seen: list[str] = []

        def ranker(query, matches):
            seen.append(query)
            return matches

        with tempfile.TemporaryDirectory() as tmp:
            engine = DurableMemoryPort(Path(tmp), "knowledge", ranker=ranker)
            engine.write({"text": "a fact"}, _valid_access())
            self.assertEqual(seen, [], "ranking ran during an authorized write")

            with self.assertRaises(PermissionError):
                engine.recall("fact", _named_but_unverified())
            self.assertEqual(
                seen, [], "the ranker saw a query from an unauthorized caller"
            )

            engine.recall("fact", _valid_access())
            self.assertEqual(seen, ["fact"], "an authorized recall must reach the ranker")

    def test_denial_precedes_query_shape_reporting(self) -> None:
        """An unauthorized caller cannot distinguish a malformed request from a denied one."""
        port = InMemoryMemoryPort("knowledge")
        with self.assertRaises(PermissionError) as ctx:
            port.recall("", _named_but_unverified())
        self.assertIn("denied or revoked", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
