#!/usr/bin/env python3
"""Compatibility entry point for the canonical execution-truth validator.

The former Sprint-0 JSON contract was removed during the documentation-triad
convergence.  Keep the command name for external callers, but validate the
living milestone/backlog/sprint ownership model instead of a nonexistent file.
"""

from __future__ import annotations

import argparse

from check_execution_truth import main as check_execution_truth


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release",
        action="store_true",
        help="Compatibility flag; receipt acceptance is validated by release evidence gates.",
    )
    parser.parse_args()
    print("ACTIVE MVP CONTRACT: superseded by canonical M-4–M-8 execution documents")
    return check_execution_truth()


if __name__ == "__main__":
    raise SystemExit(main())
