"""Cassette loader and bit-for-bit replay engine for captured LLM sessions."""

from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class CassetteStep:
    request_sha256: str
    response_body: bytes
    status_code: int
    content_type: str
    is_stream: bool


class Cassette:
    def __init__(self, steps: Dict[str, CassetteStep]) -> None:
        self.steps = steps

    @classmethod
    def load(cls, path: Path | str) -> Cassette:
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError(f"Cassette file not found: {path}")

        steps: dict[str, CassetteStep] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            req_hash = item["request_sha256"]
            raw_b64 = item.get("response_b64", "")
            raw_bytes = base64.b64decode(raw_b64.encode("ascii"))
            steps[req_hash] = CassetteStep(
                request_sha256=req_hash,
                response_body=raw_bytes,
                status_code=item.get("status_code", 200),
                content_type=item.get("content_type", "application/json"),
                is_stream=item.get("is_stream", False),
            )
        return cls(steps=steps)

    def replay(self, request_bytes: bytes) -> Optional[CassetteStep]:
        req_hash = hashlib.sha256(request_bytes).hexdigest()
        return self.steps.get(req_hash)
