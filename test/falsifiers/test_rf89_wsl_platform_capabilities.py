"""RF-89 (ADR-0089, accepted 2026-08-24): platform qualification by capability probes, not OS name.

A qualified WSL2 host must not be denied merely because its OS/kernel string contains 'microsoft'
or 'WSL'; conversely, an unqualified WSL1 or container host missing user namespaces must not
claim full containment.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch

from vanguard.packages.adapters.sandbox.platform import PlatformCapabilities, discover_platform


class RF89WSLPlatformCapabilitiesFalsifier(unittest.TestCase):
    def test_wsl2_with_bwrap_and_userns_qualifies_full(self) -> None:
        with patch("platform.system", return_value="Linux"), \
             patch("platform.release", return_value="6.18.33.2-microsoft-standard-WSL2"), \
             patch("platform.machine", return_value="x86_64"), \
             patch("shutil.which", return_value="/usr/bin/bwrap"), \
             patch("vanguard.packages.adapters.sandbox.platform._check_bwrap", return_value=("/usr/bin/bwrap", "bubblewrap 0.9.0")), \
             patch("vanguard.packages.adapters.sandbox.platform._check_user_namespaces", return_value=True):
            caps = discover_platform()
            self.assertTrue(caps.is_wsl)
            self.assertEqual(caps.wsl_version, 2)
            self.assertEqual(caps.enforcement, "full")
            self.assertEqual(caps.blockers, ())

    def test_wsl1_refuses_containment_with_actionable_blocker(self) -> None:
        with patch("platform.system", return_value="Linux"), \
             patch("platform.release", return_value="4.4.0-19041-Microsoft"), \
             patch("platform.machine", return_value="x86_64"), \
             patch("shutil.which", return_value="/usr/bin/bwrap"), \
             patch("vanguard.packages.adapters.sandbox.platform._check_bwrap", return_value=("/usr/bin/bwrap", "bubblewrap 0.9.0")), \
             patch("vanguard.packages.adapters.sandbox.platform._check_user_namespaces", return_value=False):
            caps = discover_platform()
            self.assertTrue(caps.is_wsl)
            self.assertEqual(caps.wsl_version, 1)
            self.assertEqual(caps.enforcement, "unavailable")
            self.assertTrue(any("WSL1 lacks Linux namespace" in b for b in caps.blockers))


if __name__ == "__main__":
    unittest.main()
