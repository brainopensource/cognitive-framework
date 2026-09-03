import test from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { expandFileReferences } from "../src/commands/context-refs.js";

test("expandFileReferences inlines the content of an existing @-referenced file", () => {
  const dir = mkdtempSync(join(tmpdir(), "tui-core-refs-"));
  try {
    writeFileSync(join(dir, "notes.txt"), "hello from notes");
    const result = expandFileReferences("summarize @notes.txt please", dir);

    assert.equal(result.references.length, 1);
    assert.equal(result.references[0]?.found, true);
    assert.equal(result.references[0]?.raw, "notes.txt");
    assert.match(result.text, /hello from notes/);
    assert.match(result.text, /summarize @notes\.txt please/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("expandFileReferences reports a missing file without throwing", () => {
  const dir = mkdtempSync(join(tmpdir(), "tui-core-refs-"));
  try {
    const result = expandFileReferences("read @nope.txt", dir);
    assert.equal(result.references[0]?.found, false);
    assert.equal(result.text, "read @nope.txt");
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("expandFileReferences truncates large files and flags truncation", () => {
  const dir = mkdtempSync(join(tmpdir(), "tui-core-refs-"));
  try {
    writeFileSync(join(dir, "big.txt"), "x".repeat(20_000));
    const result = expandFileReferences("@big.txt", dir);
    assert.equal(result.references[0]?.truncated, true);
    assert.match(result.text, /\[truncated\]/);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("expandFileReferences leaves plain text with no @refs untouched", () => {
  const result = expandFileReferences("just a normal prompt", "/tmp");
  assert.equal(result.text, "just a normal prompt");
  assert.deepEqual(result.references, []);
});
