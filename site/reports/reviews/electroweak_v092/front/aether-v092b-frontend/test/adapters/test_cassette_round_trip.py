import unittest
from vanguard.packages.adapters.models.cassette import CassetteRecorder, CassettePlayer
from vanguard.packages.agency.episode.state import parse_proposal, ProposalKind

class TestCassetteRoundTrip(unittest.TestCase):
    def test_canonical_proposal_recorded_and_replayed(self) -> None:
        recorder = CassetteRecorder()
        context = {"layers": [], "messages": [{"role": "user", "content": "fix bug"}]}
        tools = [{"verb": "fs.read", "name": "read", "schema": {"type": "object", "properties": {"path": {"type": "string"}}}}]
        sampling = {"temperature": 0.0}
        canonical_proposal = {
            "kind": "effect",
            "action": "fs.read",
            "args": {"path": "lru/cache.py"},
            "resource": {"kind": "fs", "root": "/workspace", "paths": ["/workspace/lru/cache.py"]},
            "text": "Reading lru/cache.py",
        }
        
        # Record interaction in canonical form
        recorder.record_interaction(context, tools, sampling, canonical_proposal)
        self.assertEqual(len(recorder.cassette.records), 1)
        
        # Playback via CassettePlayer
        player = CassettePlayer(recorder.cassette)
        res = player.propose(context, tools, sampling)
        self.assertTrue(res.ok)
        
        # Proposal parsing must succeed without ProposalMalformed
        parsed = parse_proposal(res.value)
        self.assertEqual(parsed.kind, ProposalKind.EFFECT)
        self.assertEqual(parsed.action, "fs.read")
        self.assertEqual(parsed.args, {"path": "lru/cache.py"})

if __name__ == "__main__":
    unittest.main()
