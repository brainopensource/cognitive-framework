from dataclasses import dataclass
from typing import Set, List

@dataclass(frozen=True)
class Capability:
    verb: str
    resource: str
    scopes: frozenset[str]

class TraitAttenuator:
    @staticmethod
    def attenuate(parent_caps: List[Capability], requested_caps: List[Capability]) -> List[Capability]:
        """Attenuates requested capabilities against parent capabilities."""
        parent_by_key = {(c.verb, c.resource): c for c in parent_caps}
        attenuated = []

        for req in requested_caps:
            key = (req.verb, req.resource)
            if key not in parent_by_key:
                continue
            parent = parent_by_key[key]
            # BUG: Performs set union instead of intersection, allowing child
            # to escalate scopes beyond parent!
            granted_scopes = parent.scopes | req.scopes
            attenuated.append(Capability(verb=req.verb, resource=req.resource, scopes=frozenset(granted_scopes)))

        return attenuated
