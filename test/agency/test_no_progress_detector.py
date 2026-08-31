import unittest
from vanguard.packages.agency.episode.state import Episode, Turn, RunTermination
# jcs import not needed


class TestNoProgressDetector(unittest.TestCase):
    def test_signature_is_blind_to_state_digest(self) -> None:
        """Turn signature must only depend on proposal, receipt, and progress signal, not state_digest."""
        turn1 = Turn(
            index=0,
            state_digest="digest_state_0",
            proposal_descriptor="prop_read_1",
            receipt_digest="receipt_1",
            progress_signal="progress_ok",
        )
        turn2 = Turn(
            index=1,
            state_digest="digest_state_1",
            proposal_descriptor="prop_read_1",
            receipt_digest="receipt_1",
            progress_signal="progress_ok",
        )
        self.assertEqual(turn1.signature, turn2.signature)

    def test_repeats_detects_identical_actions(self) -> None:
        """Episode.repeats() returns True when limit consecutive turns share identical signature."""
        ep = Episode(episode_id="ep-1", run_id="run-1", principal="agent-1")
        
        turn1 = Turn(index=0, state_digest="s0", proposal_descriptor="p1", receipt_digest="r1", progress_signal="sig")
        ep = ep.with_turn(turn1)
        
        turn2 = Turn(index=1, state_digest="s1", proposal_descriptor="p1", receipt_digest="r1", progress_signal="sig")
        ep = ep.with_turn(turn2)
        
        turn3 = Turn(index=2, state_digest="s2", proposal_descriptor="p1", receipt_digest="r1", progress_signal="sig")
        self.assertTrue(ep.repeats(turn3, limit=3))

    def test_different_receipts_do_not_trigger_repeats(self) -> None:
        """Polling or successive command runs with differing receipts are not repeats."""
        ep = Episode(episode_id="ep-1", run_id="run-1", principal="agent-1")
        
        turn1 = Turn(index=0, state_digest="s0", proposal_descriptor="p1", receipt_digest="r1", progress_signal="sig")
        ep = ep.with_turn(turn1)
        
        turn2 = Turn(index=1, state_digest="s1", proposal_descriptor="p1", receipt_digest="r2", progress_signal="sig")
        ep = ep.with_turn(turn2)
        
        turn3 = Turn(index=2, state_digest="s2", proposal_descriptor="p1", receipt_digest="r3", progress_signal="sig")
        self.assertFalse(ep.repeats(turn3, limit=3))


if __name__ == "__main__":
    unittest.main()
