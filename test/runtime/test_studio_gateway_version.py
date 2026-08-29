from __future__ import annotations

import unittest
from importlib.metadata import PackageNotFoundError
from unittest.mock import patch

from vanguard.packages.runtime.service.studio_gateway import _package_version


class TestStudioGatewayVersion(unittest.TestCase):
    @patch(
        "vanguard.packages.runtime.service.studio_gateway.distribution_version",
        return_value="0.9.0b1",
    )
    def test_version_comes_from_installed_distribution(self, _version: object) -> None:
        self.assertEqual(_package_version(), "0.9.0b1")

    @patch(
        "vanguard.packages.runtime.service.studio_gateway.distribution_version",
        side_effect=PackageNotFoundError,
    )
    def test_uninstalled_source_tree_uses_vanguard_version(self, _version: object) -> None:
        self.assertEqual(_package_version(), "0.9.0b1")
