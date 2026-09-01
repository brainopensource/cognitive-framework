import json
from typing import List, Dict, Any

class SSEDecoder:
    def __init__(self):
        self._buffer = ""

    def feed(self, chunk: bytes) -> List[Dict[str, Any]]:
        self._buffer += chunk.decode("utf-8")
        lines = self._buffer.split("\n")
        self._buffer = lines[-1]  # Keep incomplete line in buffer

        events = []
        for line in lines[:-1]:
            line = line.strip()
            if line.startswith("data: "):
                data_str = line[6:].strip()
                if data_str == "[DONE]":
                    events.append({"done": True})
                else:
                    try:
                        events.append(json.loads(data_str))
                    except Exception:
                        pass
        return events

    def close(self) -> List[Dict[str, Any]]:
        # BUG: When close() is called at EOF, the remaining buffer in self._buffer
        # is discarded without being parsed, dropping the final event chunk!
        self._buffer = ""
        return []
