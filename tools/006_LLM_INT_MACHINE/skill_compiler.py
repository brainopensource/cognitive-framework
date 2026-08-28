"""Dynamic Skill & Toolchain Compiler (Hermes-Style Closed-Loop Autonomous Learning).

Allows the agentic harness to synthesize, test, and dynamically register new tool helpers
during execution:
Turns repeated multi-turn search/patch subroutines into compiled, deterministic tools.
"""

from __future__ import annotations
import ast
import inspect
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping


@dataclass
class CompiledSkill:
    skill_name: str
    description: str
    code_body: str
    is_validated: bool = False
    validation_error: str = ""
    invocations_count: int = 0


class DynamicSkillCompiler:
    """Synthesizes, tests, and injects runtime tools into the active ToolWorkspace."""

    def __init__(self, workspace_root: Path):
        self.root = workspace_root
        self.skills_dir = self.root / ".skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self.registry: dict[str, CompiledSkill] = {}

    def compile_and_register_skill(
        self,
        skill_name: str,
        description: str,
        python_code: str,
        test_assertion: Callable[[], bool] | None = None,
    ) -> tuple[bool, str]:
        # 1. Syntax check via AST
        try:
            tree = ast.parse(python_code, filename=f"<dynamic_skill_{skill_name}>")
        except SyntaxError as e:
            return False, f"Syntax Error in dynamic skill '{skill_name}': {str(e)}"

        # 2. Execute and validate in isolated local scope
        local_scope: dict[str, Any] = {}
        try:
            exec(compile(tree, filename=f"<skill_{skill_name}>", mode="exec"), {}, local_scope)
        except Exception as e:
            return False, f"Runtime error initializing skill '{skill_name}': {str(e)}"

        # 3. Verify test assertion if provided
        if test_assertion:
            try:
                if not test_assertion():
                    return False, f"Validation assertion failed for dynamic skill '{skill_name}'"
            except Exception as e:
                return False, f"Validation test raised exception: {str(e)}"

        # 4. Save to persistent skills directory
        skill_file = self.skills_dir / f"{skill_name}.py"
        skill_file.write_text(python_code, encoding="utf-8")

        compiled = CompiledSkill(
            skill_name=skill_name,
            description=description,
            code_body=python_code,
            is_validated=True,
        )
        self.registry[skill_name] = compiled
        return True, f"Successfully compiled and registered dynamic skill '{skill_name}'"

    def execute_skill(self, skill_name: str, **kwargs: Any) -> Any:
        skill = self.registry.get(skill_name)
        if not skill:
            raise KeyError(f"Dynamic skill '{skill_name}' not found in registry.")

        local_scope: dict[str, Any] = {}
        exec(skill.code_body, {}, local_scope)
        target_fn = local_scope.get(skill_name)
        if not callable(target_fn):
            raise TypeError(f"Skill '{skill_name}' does not expose a callable function named '{skill_name}'")

        skill.invocations_count += 1
        return target_fn(**kwargs)

    def list_registered_skills(self) -> list[dict[str, Any]]:
        return [
            {
                "name": s.skill_name,
                "description": s.description,
                "invocations": s.invocations_count,
            }
            for s in self.registry.values()
        ]
