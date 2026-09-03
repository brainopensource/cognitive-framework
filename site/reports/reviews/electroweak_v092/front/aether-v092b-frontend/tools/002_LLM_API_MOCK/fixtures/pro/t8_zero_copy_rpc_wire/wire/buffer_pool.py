import threading
from typing import Optional

class BufferExhaustedError(RuntimeError):
    pass

class BufferPool:
    def __init__(self, block_size: int = 4096, max_blocks: int = 16):
        self.block_size = block_size
        self.max_blocks = max_blocks
        self._lock = threading.Lock()
        self._available = [bytearray(block_size) for _ in range(max_blocks)]
        self._allocated = 0

    def acquire(self) -> bytearray:
        with self._lock:
            if not self._available:
                raise BufferExhaustedError("no available buffers in pool")
            self._allocated += 1
            return self._available.pop()

    def release(self, buf: bytearray) -> None:
        with self._lock:
            if len(self._available) < self.max_blocks:
                self._available.append(buf)
                self._allocated = max(0, self._allocated - 1)

    @property
    def in_use(self) -> int:
        with self._lock:
            return self._allocated
