from typing import List
from .traits import Capability, TraitAttenuator

class AgentNode:
    def __init__(self, name: str, capabilities: List[Capability]):
        self.name = name
        self.capabilities = capabilities

    def spawn_child(self, child_name: str, requested_caps: List[Capability]) -> "AgentNode":
        effective_caps = TraitAttenuator.attenuate(self.capabilities, requested_caps)
        return AgentNode(child_name, effective_caps)
