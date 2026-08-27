#!/usr/bin/env python3
"""Fail closed when hermetic test commands inherit live provider credentials."""

from __future__ import annotations

import os


PROVIDER_KEYS = (
    "OPENROUTER_API_KEY",
    "DEEPSEEK_API_KEY",
    "OPENAI_API_KEY",
)


def exported_provider_keys() -> tuple[str, ...]:
    return tuple(key for key in PROVIDER_KEYS if os.environ.get(key))


def main() -> int:
    leaked = exported_provider_keys()
    if leaked:
        for key in leaked:
            print(f"TEST HYGIENE FAIL: {key} is set; hermetic suites require provider keys unset")
        return 1
    print("TEST HYGIENE PASS: provider keys are unset")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
