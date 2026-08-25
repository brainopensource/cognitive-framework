"""Polyglot Test Runner ported from LEX to Vanguard.
Detects project build manifests across Python, Rust, Go, JavaScript/TypeScript, Java, C/C++.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional, Tuple


class LexPolyglotReproducer:
    """Detects project framework and constructs resilient test commands."""

    @staticmethod
    def detect_framework(workspace_root: Path) -> str:
        """Inspects workspace build manifests to identify the test framework."""
        root = Path(workspace_root)

        # Rust Cargo
        if (root / "Cargo.toml").exists():
            return "RustCargo"

        # Go Test
        if (root / "go.mod").exists():
            return "GoTest"

        # JS / TS
        if (root / "vitest.config.ts").exists() or (root / "vitest.config.js").exists():
            return "JavaScriptVitest"
        if (root / "jest.config.js").exists() or (root / "jest.config.ts").exists():
            return "JavaScriptJest"
        if (root / "pnpm-lock.yaml").exists():
            return "JavaScriptPnpm"
        if (root / "yarn.lock").exists():
            return "JavaScriptYarn"
        if (root / "package.json").exists():
            return "JavaScriptNpm"

        # Java
        if (root / "pom.xml").exists():
            return "JavaMaven"
        if (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
            return "JavaGradle"

        # C / C++ / Makefile
        if (root / "CMakeLists.txt").exists():
            return "CppCtest"
        if (root / "Makefile").exists():
            return "Makefile"

        # Python
        if (root / "poetry.lock").exists():
            return "PythonPoetry"
        if (root / "uv.lock").exists():
            return "PythonUv"
        if (root / "tox.ini").exists():
            return "PythonTox"
        if (root / "pytest.ini").exists():
            return "PythonPytest"

        return "PythonAuto"

    @classmethod
    def build_test_command(cls, workspace_root: Path, target: Optional[str] = None) -> Tuple[List[str], str]:
        """Constructs the command arguments and description for test execution."""
        framework = cls.detect_framework(workspace_root)

        if framework == "RustCargo":
            cmd = ["cargo", "test"] if not target else ["cargo", "test", "--", target]
        elif framework == "GoTest":
            cmd = ["go", "test", "-v", "./..."] if not target else ["go", "test", "-v", target]
        elif framework == "JavaScriptVitest":
            cmd = ["npx", "vitest", "run"] if not target else ["npx", "vitest", "run", target]
        elif framework == "JavaScriptJest":
            cmd = ["npx", "jest"] if not target else ["npx", "jest", target]
        elif framework == "JavaScriptNpm":
            cmd = ["npm", "test"] if not target else ["npm", "test", "--", target]
        elif framework == "JavaMaven":
            cmd = ["mvn", "test"] if not target else ["mvn", "test", f"-Dtest={target}"]
        elif framework == "Makefile":
            cmd = ["make", "test"] if not target else ["make", target]
        else:
            # Python auto fallback (pytest if available, otherwise unittest)
            if target:
                cmd = ["sh", "-c", f"python3 -m pytest -v {target} 2>/dev/null || python3 -m unittest {target}"]
            else:
                cmd = ["sh", "-c", "python3 -m pytest -v 2>/dev/null || python3 -m unittest discover tests"]

        return cmd, framework
