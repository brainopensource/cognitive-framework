"""Unit and Integration tests for the LAM Mock Server and Catalog Engine."""

from __future__ import annotations

import json
import socket
import threading
import time
import urllib.request
from pathlib import Path

from catalog import Catalog, load_catalog, select_reply, select_tool_step
from mock_server import run_server


def test_catalog_loader() -> None:
    catalog_dir = Path(__file__).resolve().parent / "answer_bank"
    catalog = load_catalog(catalog_dir)
    assert "math_formula_v1" in catalog.scenarios
    assert "slugify_repair_v1" in catalog.scenarios
    assert catalog.default_key == "math_formula_v1"
    assert len(catalog.sha256) == 64
    print("✔ test_catalog_loader passed")


def test_stateless_multi_turn_advancement() -> None:
    catalog_dir = Path(__file__).resolve().parent / "answer_bank"
    catalog = load_catalog(catalog_dir)
    scenario = catalog.scenarios["math_formula_v1"]

    # Turn 1: Initial prompt (no prior reply in history)
    sel_1 = select_reply(scenario, effective_tier=2, prompt="Please calculate (A + B) * B")
    assert sel_1.requested_turn == 1
    assert sel_1.matched_reply is None
    assert sel_1.reply.turn == 1
    assert "+ B" in sel_1.reply.text  # Tier 2 turn 1 is intentionally buggy

    # Turn 2: Conversation history includes Turn 1's buggy response
    history_turn_2 = f"Please calculate (A + B) * B\n{sel_1.reply.text}\nError: Expected multiplication, got addition!"
    sel_2 = select_reply(scenario, effective_tier=2, prompt=history_turn_2)
    assert sel_2.requested_turn == 2
    assert sel_2.matched_reply is not None
    assert sel_2.matched_reply.turn == 1
    assert sel_2.reply.turn == 2
    assert "* B" in sel_2.reply.text  # Tier 2 turn 2 fixed the bug!

    # Turn 3: Exhaustion repeat_last
    history_turn_3 = f"{history_turn_2}\n{sel_2.reply.text}\nAll tests passed!"
    sel_3 = select_reply(scenario, effective_tier=2, prompt=history_turn_3)
    assert sel_3.requested_turn == 3
    assert sel_3.exhausted is True
    assert sel_3.reply.turn == 2

    print("✔ test_stateless_multi_turn_advancement passed")


def test_tool_results_counting() -> None:
    catalog_dir = Path(__file__).resolve().parent / "answer_bank"
    catalog = load_catalog(catalog_dir)
    scenario = catalog.scenarios["math_formula_v1"]

    # 0 tool results seen -> Turn 1
    sel_1 = select_tool_step(scenario, effective_tier=4, tool_results_seen=0)
    assert sel_1.requested_turn == 1
    assert len(sel_1.reply.tool_calls) > 0
    assert sel_1.reply.tool_calls[0].name == "apply_patch"

    # 1 tool result seen -> Turn 2
    sel_2 = select_tool_step(scenario, effective_tier=4, tool_results_seen=1)
    assert sel_2.requested_turn == 2
    assert "passes all test validations" in sel_2.reply.text

    print("✔ test_tool_results_counting passed")


def test_mock_server_endpoints() -> None:
    from http.server import HTTPServer
    from mock_server import MockServerHandler

    catalog_dir = Path(__file__).resolve().parent / "answer_bank"
    port = 4148

    catalog = load_catalog(catalog_dir)
    MockServerHandler.catalog = catalog
    MockServerHandler.cassette = None
    MockServerHandler.recorder = None
    MockServerHandler.latency_ms = 0
    MockServerHandler.default_tier = 2

    server = HTTPServer(("127.0.0.1", port), MockServerHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    time.sleep(0.2)

    try:
        # 1. Health check
        req = urllib.request.Request(f"http://127.0.0.1:{port}/health")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert data["status"] == "ok"
            assert data["catalog_sha256"] is not None

        # 2. Models list
        req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/models")
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            assert len(data["data"]) > 0

        # 3. Chat completion - Turn 1 (Tier 2 default)
        body_turn1 = json.dumps({
            "model": "qwen3.6:27b",  # mapped to Tier 2
            "messages": [{"role": "user", "content": "Write calculated_value = (A + B) * B"}],
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/chat/completions",
            data=body_turn1,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content_turn1 = data["choices"][0]["message"]["content"]
            assert "+ B" in content_turn1

        # 4. Chat completion - Turn 2 (Feedback in history)
        body_turn2 = json.dumps({
            "model": "qwen3.6:27b",
            "messages": [
                {"role": "user", "content": "Write calculated_value = (A + B) * B"},
                {"role": "assistant", "content": content_turn1},
                {"role": "user", "content": "Error: you added B instead of multiplying by B!"},
            ],
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/chat/completions",
            data=body_turn2,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content_turn2 = data["choices"][0]["message"]["content"]
            assert "* B" in content_turn2

        # 5. SSE Streaming check
        body_stream = json.dumps({
            "model": "qwen3.6:27b",
            "messages": [{"role": "user", "content": "Write calculated_value = (A + B) * B"}],
            "stream": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/v1/chat/completions",
            data=body_stream,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            chunks = resp.read().decode("utf-8").split("\n\n")
            assert len(chunks) > 2
            assert any("[DONE]" in c for c in chunks)

        print("✔ test_mock_server_endpoints passed")
    finally:
        server.shutdown()
        server.server_close()



if __name__ == "__main__":
    test_catalog_loader()
    test_stateless_multi_turn_advancement()
    test_tool_results_counting()
    test_mock_server_endpoints()
    print("\n🎉 ALL LAM MOCK TESTS PASSED SUCCESSFULLY!")
