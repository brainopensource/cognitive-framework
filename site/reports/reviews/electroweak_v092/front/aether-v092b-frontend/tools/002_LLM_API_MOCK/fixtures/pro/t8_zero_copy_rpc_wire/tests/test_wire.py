import unittest
from wire.buffer_pool import BufferPool, BufferExhaustedError
from wire.framer import Frame, FrameDecoder, FrameEncoder, ChecksumMismatchError

class TestZeroCopyWire(unittest.TestCase):
    def test_encode_and_single_frame_decode(self):
        encoded = FrameEncoder.encode(msg_id=101, payload=b"hello-world-rpc")
        decoder = FrameDecoder()
        frames = decoder.feed(encoded)
        self.assertEqual(len(frames), 1)
        self.assertEqual(frames[0].msg_id, 101)
        self.assertEqual(frames[0].payload, b"hello-world-rpc")

    def test_chunked_stream_fragment_reassembly(self):
        encoded = FrameEncoder.encode(msg_id=202, payload=b"streaming-payload-across-three-chunks")
        decoder = FrameDecoder()
        # Split into 3 fragments
        p1, p2, p3 = encoded[:5], encoded[5:20], encoded[20:]
        self.assertEqual(decoder.feed(p1), [])
        self.assertEqual(decoder.feed(p2), [])
        f3 = decoder.feed(p3)
        self.assertEqual(len(f3), 1)
        self.assertEqual(f3[0].msg_id, 202)
        self.assertEqual(f3[0].payload, b"streaming-payload-across-three-chunks")

    def test_checksum_corruption_detection(self):
        encoded = bytearray(FrameEncoder.encode(msg_id=303, payload=b"critical-data"))
        encoded[len(encoded) - 10] ^= 0xFF # corrupt payload
        decoder = FrameDecoder()
        with self.assertRaises(ChecksumMismatchError):
            decoder.feed(bytes(encoded))

    def test_buffer_pool_recycling(self):
        pool = BufferPool(block_size=1024, max_blocks=2)
        b1 = pool.acquire()
        b2 = pool.acquire()
        self.assertEqual(pool.in_use, 2)
        with self.assertRaises(BufferExhaustedError):
            pool.acquire()
        pool.release(b1)
        self.assertEqual(pool.in_use, 1)
        b3 = pool.acquire()
        self.assertEqual(pool.in_use, 2)

if __name__ == "__main__":
    unittest.main()
