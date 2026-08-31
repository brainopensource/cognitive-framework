import unittest
from src.traits import Capability, TraitAttenuator
from src.agent_node import AgentNode

class TestTraitAttenuation(unittest.TestCase):
    def test_child_cannot_escalate_capabilities(self):
        parent_caps = [
            Capability("fs.read", "/workspace", frozenset(["read:view"]))
        ]
        parent = AgentNode("parent-agent", parent_caps)

        # Child requests write and admin scopes
        requested = [
            Capability("fs.read", "/workspace", frozenset(["read:view", "write:modify", "admin:all"]))
        ]
        child = parent.spawn_child("child-agent", requested)

        self.assertEqual(len(child.capabilities), 1)
        child_cap = child.capabilities[0]
        # Falsifier Assertion: Child MUST ONLY have the intersection (read:view)
        self.assertEqual(
            child_cap.scopes,
            frozenset(["read:view"]),
            f"Escalation detected: child scopes {child_cap.scopes} exceed parent scopes {parent_caps[0].scopes}"
        )

if __name__ == "__main__":
    unittest.main()
