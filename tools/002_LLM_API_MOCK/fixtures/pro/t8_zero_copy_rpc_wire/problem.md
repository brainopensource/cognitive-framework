# Problem: Zero-Copy Binary RPC Wire Protocol & Frame Reassembly (Tier 8)

Implement a high-throughput length-prefixed zero-copy binary RPC framing engine with payload checksumming, ring buffer memory recycling, and stream chunk reassembly.

### Requirements:
1. Frame format: `[MAGIC: 2B][MSG_ID: 4B][FLAGS: 2B][PAYLOAD_LEN: 4B][PAYLOAD: N bytes][CRC32: 4B]`.
2. `BufferPool` must allocate fixed-size bytearrays from a pre-allocated ring buffer and return them via `release()` to avoid GC pressure.
3. `FrameDecoder` must handle fragmented TCP stream chunks (e.g. half a header in packet 1, rest of payload in packet 2) without copying payload bytes into intermediate strings.
4. Validate CRC32 checksums on frame payloads; corrupted frames must raise `ChecksumMismatchError`.
