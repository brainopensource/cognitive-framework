"""Mock LLM API Stub - OpenAPI/OpenAI-compatible generic stub response."""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict


class MockLLMStub:
    """Provides standard OpenAPI/OpenAI chat-completion dictionary payloads."""

    DEFAULT_MESSAGE = (
        "this is not your answer, this is only a mocked llm api response stub, "
        "route correctly for the right llm api"
    )

    def __init__(self, message: str = DEFAULT_MESSAGE) -> None:
        self.message = message

    def generate(self, prompt: str, model: str = "mock-model-v1", **kwargs: Any) -> Dict[str, Any]:
        prompt_tokens = max(1, len(prompt.split()))
        completion_tokens = max(1, len(self.message.split()))
        return {
            "id": f"chatcmpl-mock-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": self.message,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
        }
