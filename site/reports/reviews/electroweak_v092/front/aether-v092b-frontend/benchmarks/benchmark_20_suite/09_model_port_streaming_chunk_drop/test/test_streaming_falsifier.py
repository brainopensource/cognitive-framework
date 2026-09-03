import unittest
from src.sse_decoder import SSEDecoder

class TestSSEDecoder(unittest.TestCase):
    def test_flushes_final_chunk_on_close(self):
        decoder = SSEDecoder()
        chunk1 = b'data: {"choices": [{"delta": {"content": "Hello"}}]}'
        # chunk2 does not have a trailing newline
        chunk2 = b'\ndata: {"choices": [{"delta": {"content": " World"}}]}'

        ev1 = decoder.feed(chunk1)
        ev2 = decoder.feed(chunk2)
        ev_final = decoder.close()

        all_events = ev1 + ev2 + ev_final
        # Falsifier Assertion: Both events must be decoded without dropping the trailing chunk
        self.assertEqual(
            len(all_events),
            2,
            f"Chunk dropped: expected 2 events, got {len(all_events)} ({all_events})"
        )
        self.assertEqual(all_events[1]["choices"][0]["delta"]["content"], " World")

if __name__ == "__main__":
    unittest.main()
