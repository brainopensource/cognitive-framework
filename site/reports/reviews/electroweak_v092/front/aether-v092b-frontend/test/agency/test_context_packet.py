import unittest

from vanguard.packages.agency.context import ContextPacketError, build_context_packet


class ContextPacketTests(unittest.TestCase):
    def test_selection_is_bounded_and_omissions_are_explicit(self) -> None:
        packet = build_context_packet(
            task_digest="sha256:task", repository_snapshot="sha256:repo",
            provider="fallback", provider_version="1", query_digest="sha256:q",
            budget_tokens=10, reserve_tokens=2,
            selected=(
                {"kind": "file", "path": "a.py", "tokens": 5},
                {"kind": "symbol", "name": "B", "tokens": 4},
            ),
        )
        self.assertEqual(packet.estimated_tokens, 5)
        self.assertEqual(packet.omissions, ("B",))
        self.assertEqual(packet.to_canonical_dict()["provider"], "fallback")

    def test_invalid_budget_fails_closed(self) -> None:
        with self.assertRaises(ContextPacketError):
            build_context_packet(
                task_digest="t", repository_snapshot="r", provider="p",
                provider_version="1", query_digest="q", budget_tokens=1,
                reserve_tokens=2,
            )


if __name__ == "__main__":
    unittest.main()
