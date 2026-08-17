"""Composition reads its values; it does not carry them as literals.

S7-A-06. Three hardcoded values in the composition root made composition a
statement about one machine rather than about the manifest:

  - `/usr/bin/bwrap` — an absolute path, so a host with bubblewrap anywhere
    else on PATH could not compose at all, and the refusal named the absence
    without naming the remedy.
  - `Reservation(usd_micros=100, millis=1000)` — a re-dispatch reservation
    invented at the call site rather than read from the frozen budget policy.
  - `approval_required_above="low"` — a literal standing in for the manifest
    component that replaces it in S8-B-04.
"""

from __future__ import annotations

import ast
import unittest
from pathlib import Path

from vanguard.packages.kernel.budget import Reservation
from vanguard.packages.runtime.root import (
    Runtime,
    CompositionError,
    _bwrap_path,
    _reservation_for,
)

ROOT_PY = Path(__file__).resolve().parents[2] / "vanguard" / "packages" / "runtime" / "root.py"


class BwrapIsProbedNotAssumed(unittest.TestCase):
    def test_bwrap_found_outside_usr_bin_is_accepted(self) -> None:
        """The failing case: bubblewrap installed somewhere other than /usr/bin."""

        found = _bwrap_path(which=lambda name: "/nix/store/abc123/bin/bwrap")
        self.assertEqual(found, "/nix/store/abc123/bin/bwrap")

    def test_bwrap_at_the_conventional_path_still_works(self) -> None:
        self.assertEqual(
            _bwrap_path(which=lambda name: "/usr/bin/bwrap"), "/usr/bin/bwrap"
        )

    def test_probe_asks_for_bwrap_by_name_not_by_path(self) -> None:
        asked: list[str] = []

        def which(name: str) -> str | None:
            asked.append(name)
            return "/usr/local/bin/bwrap"

        _bwrap_path(which=which)
        self.assertEqual(asked, ["bwrap"])

    def test_absent_bwrap_raises_and_names_the_remedy(self) -> None:
        with self.assertRaises(CompositionError) as caught:
            _bwrap_path(which=lambda name: None)
        message = str(caught.exception)
        # A refusal that only reports the absence leaves the operator guessing.
        self.assertIn("bwrap", message)
        self.assertIn("PATH", message)
        self.assertIn("bubblewrap", message.lower())

    def test_no_absolute_bwrap_literal_remains_in_the_composition_root(self) -> None:
        source = ROOT_PY.read_text(encoding="utf-8")
        self.assertNotIn("/usr/bin/bwrap", source)


class ReservationComesFromTheBudgetPolicy(unittest.TestCase):
    def test_reservation_is_one_effects_share_of_the_ceiling(self) -> None:
        reservation = _reservation_for({"usd_micros": 5_000, "millis": 30_000}, 10)
        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.usd_micros, 500)
        self.assertEqual(reservation.millis, 3_000)

    def test_two_policies_give_two_reservations(self) -> None:
        """The whole point: the value tracks the manifest, not the call site."""

        lean = _reservation_for({"usd_micros": 10_000, "millis": 100_000}, 100)
        rich = _reservation_for({"usd_micros": 900_000, "millis": 60_000}, 4)
        self.assertNotEqual(lean.as_map(), rich.as_map())

    def test_whole_ceiling_is_not_reserved_for_one_dispatch(self) -> None:
        """Reserving everything is derived too -- and denies the second effect."""

        ceilings = {"usd_micros": 1_000_000, "millis": 1_800_000}
        reservation = _reservation_for(ceilings, 128)
        self.assertLess(reservation.usd_micros, ceilings["usd_micros"])
        self.assertLess(reservation.millis, ceilings["millis"])

    def test_missing_dimension_reserves_nothing_rather_than_inventing(self) -> None:
        reservation = _reservation_for({}, 8)
        self.assertEqual(reservation.usd_micros, 0)
        self.assertEqual(reservation.millis, 0)

    def test_composed_manifests_supply_their_own_effect_budget(self) -> None:
        """F-12: the count comes from the policy, not from root.py."""

        from vanguard.packages.runtime.root import Runtime

        default = Runtime.compose("vg-code-default", episode_id="e1")
        shell = Runtime.compose("vg-shell-only", episode_id="e1")
        self.assertEqual(default.effect_budget, 128)
        self.assertEqual(shell.effect_budget, 64)

    def test_policy_without_an_effect_bound_is_not_treated_as_generous(self) -> None:
        self.assertEqual(Runtime._effect_budget("{}", "policy.json"), 1)

    def test_no_literal_reservation_remains_in_the_composition_root(self) -> None:
        source = ROOT_PY.read_text(encoding="utf-8")
        self.assertNotIn("Reservation(usd_micros=100, millis=1000)", source)


class ApprovalThresholdIsMarkedForHandoff(unittest.TestCase):
    def test_approval_literal_carries_a_pointer_to_its_replacement(self) -> None:
        """S7-A-06 step 4: mark, do not implement. S8-B-04 owns the change."""

        source = ROOT_PY.read_text(encoding="utf-8")
        tree = ast.parse(source)
        line = None
        for node in ast.walk(tree):
            if isinstance(node, ast.keyword) and node.arg == "approval_required_above":
                line = node.value.lineno
                break
        self.assertIsNotNone(line, "approval_required_above not found in root.py")

        lines = source.splitlines()
        window = "\n".join(lines[max(0, line - 12) : line])
        self.assertIn("TODO(S8-B-04)", window)


if __name__ == "__main__":
    unittest.main()
