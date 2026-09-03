"""RF-87 (ADR-0089): execution-profile identity in D_R.

A change to effective execution profile must change D_R (run_digest), and profile selection
must be reflected in RunPlan identity.
"""

from __future__ import annotations

import unittest
from vanguard.packages.domain.canonicalisation.digest import digest_of
from vanguard.packages.runtime.activation import ActivationPlan, ActivationStep
from vanguard.packages.runtime.profiles import PRESETS, resolve_profile
from vanguard.packages.runtime.run_plan import RunPlan, plan_run


class RF87ExecutionProfileIdentityFalsifier(unittest.TestCase):
    def _dummy_activation(self) -> ActivationPlan:
        step = ActivationStep(
            name="test-comp",
            interface="mhf.model/1",
            isolation="in-process",
            ceiling=(),
            requires=(),
        )
        return ActivationPlan("sha256:" + "0" * 64, (step,))

    def test_changing_profile_changes_run_digest(self) -> None:
        activation = self._dummy_activation()
        profile_local = resolve_profile("local")
        profile_hermetic = resolve_profile("hermetic")
        
        plan_local = plan_run(
            activation,
            project_id="p1",
            run_id="r1",
            episode_id="e1",
            task="do task",
            profile=profile_local,
        )
        plan_hermetic = plan_run(
            activation,
            project_id="p1",
            run_id="r1",
            episode_id="e1",
            task="do task",
            profile=profile_hermetic,
        )
        self.assertNotEqual(plan_local.run_digest, plan_hermetic.run_digest)
        self.assertEqual(plan_local.profile_id, "local")
        self.assertEqual(plan_hermetic.profile_id, "hermetic")
        self.assertEqual(plan_local.profile_digest, profile_local.digest)
        self.assertEqual(plan_hermetic.profile_digest, profile_hermetic.digest)


if __name__ == "__main__":
    unittest.main()
