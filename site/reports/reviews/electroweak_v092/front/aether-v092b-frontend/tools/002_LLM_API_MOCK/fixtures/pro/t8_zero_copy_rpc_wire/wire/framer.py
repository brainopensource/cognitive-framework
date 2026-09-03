import struct
import zlib
from typing import List, Optional, Tuple
from dataclasses import dataclass

MAGIC_HEADER = 0xAA55
HEADER_FORMAT = "!HII" # Magic (2B), MsgId (4B), PayloadLen (4B)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
FOOTER_SIZE = 4 # CRC32

class ChecksumMismatchError(ValueError):
    pass

@dataclass
class Frame:
    msg_id: int
    payload: bytes

class FrameEncoder:
    @staticmethod
    def encode(msg_id: int, payload: bytes) -> bytes:
        crc = zlib.crc32(payload)
        header = struct.pack(HEADER_FORMAT, MAGIC_HEADER, msg_id, len(payload))
        footer = struct.pack("!I", crc)
        return header + payload + footer

class FrameDecoder:
    def __init__(self):
        self._buffer = bytearray()

    def feed(self, chunk: bytes) -> List[Frame]:
        # BENCHMARK SKELETON: Stub implementation with fragmented frame bug
        self._buffer.extend(chunk)
        frames = []
        while len(self._buffer) >= HEADER_SIZE + FOOTER_SIZE:
            magic, msg_id, length = struct.unpack_from(HEADER_FORMAT, self._buffer, 0)
            if magic != MAGIC_HEADER:
                raise ValueError("Invalid magic header")
            total_size = HEADER_SIZE + length + FOOTER_SIZE
            if len(self._buffer) < total_size:
                break
            payload = bytes(self._buffer[HEADER_SIZE:HEADER_SIZE + length])
            crc_received = struct.unpack_from("!I", self._buffer, HEADER_SIZE + length)[0]
            if zlib.crc32(payload) != crc_received:
                raise ChecksumMismatchError("CRC32 mismatch")
            frames.append(Frame(msg_id=msg_id, payload=payload))
            self._buffer = self._buffer[total_size:]
        return frames
