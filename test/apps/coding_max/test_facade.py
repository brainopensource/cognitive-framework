from __future__ import annotations

import inspect
import unittest
from pathlib import Path
from unittest.mock import Mock

from vanguard.packages.apps.coding_max.facade import CodingMaxFacade, InvalidPreset
from vanguard.packages.runtime.app_service import ApplicationService
from vanguard.packages.runtime.results import RunResult, StatusResult


class CodingMaxFacadeTests(unittest.TestCase):
    def test_invalid_preset_is_rejected(self) -> None:
        facade = CodingMaxFacade(service=Mock(spec=ApplicationService))
        with self.assertRaises(InvalidPreset):
            facade.run("task", preset="unknown")

    def test_run_status_resume_evidence_and_cost_delegate(self) -> None:
        service = Mock(spec=ApplicationService)
        service.run.return_value = RunResult("r", "completed", "complete", 1, None, "")
        service.status.return_value = StatusResult("r", "completed", 1, 1, None, ".")
        facade = CodingMaxFacade(service=service)
        self.assertIs(facade.run("task", preset="fast"), service.run.return_value)
        self.assertIs(facade.status("r"), service.status.return_value)
        facade.resume("r")
        facade.evidence("r")
        facade.cost("r")
        service.resume.assert_called_once()
        service.evidence.assert_called_once()
        service.cost.assert_called_once()

    def test_app_code_has_no_provider_or_process_imports(self) -> None:
        source = inspect.getsource(CodingMaxFacade)
        self.assertNotIn("subprocess", source)
        self.assertNotIn("openrouter", source.lower())
        self.assertNotIn("ollama", source.lower())


if __name__ == "__main__":
    unittest.main()
