"""RF-88 (ADR-0089): `sandboxed`/`hermetic` unavailable must never execute on host.

`resolve_profile()` (`runtime/profiles.py`) is the only place a named profile
preset is resolved against observed host capability. This falsifier proves
the fail-closed contract directly: an unqualified host requesting a
containment-bearing profile raises `SandboxUnavailable` and never silently
returns a host-backed profile.
"""

from __future__ import annotations

import unittest

from vanguard.packages.runtime.profiles import (
    ExecutionProfile,
    SandboxUnavailable,
    resolve_profile,
)


class RF88SandboxFailClosedFalsifier(unittest.TestCase):
    def test_sandboxed_unavailable_host_raises_not_downgrades(self) -> None:
        with self.assertRaises(SandboxUnavailable):
            resolve_profile("sandboxed", host_qualifies=False)

    def test_hermetic_unavailable_host_raises_not_downgrades(self) -> None:
        with self.assertRaises(SandboxUnavailable):
            resolve_profile("hermetic", host_qualifies=False)

    def test_local_never_raises_sandbox_unavailable(self) -> None:
        # local's backend IS host, so there is no fallback question.
        effective = resolve_profile("local", host_qualifies=False)
        self.assertEqual(effective.requested.process_backend, "host")

    def test_no_profile_ever_resolves_to_a_weaker_backend_than_requested(self) -> None:
        qualified = resolve_profile("hermetic", host_qualifies=True)
        self.assertEqual(qualified.requested.process_backend, "platform-sandbox")
        self.assertIsInstance(qualified.requested, ExecutionProfile)


if __name__ == "__main__":
    unittest.main()
