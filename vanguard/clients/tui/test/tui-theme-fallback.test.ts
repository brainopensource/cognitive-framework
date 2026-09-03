import { test } from "node:test";
import assert from "node:assert/strict";
import {
  detectColorMode,
  styleToAnsi,
  rgbToAnsi256,
  rgbToAnsi16,
  hexToRgb,
  DEFAULT_THEME,
} from "../src/theme.js";
import { computeUsageBar, tierStyle } from "../src/components/usage-bar.js";

test("detectColorMode: NO_COLOR and TERM=dumb force plain", () => {
  assert.equal(detectColorMode({ NO_COLOR: "1" }), "plain");
  assert.equal(detectColorMode({ TERM: "dumb" }), "plain");
});

test("detectColorMode: COLORTERM=truecolor wins regardless of TERM", () => {
  assert.equal(detectColorMode({ COLORTERM: "truecolor", TERM: "xterm" }), "truecolor");
});

test("detectColorMode: xterm-256color without COLORTERM is 256color, not truecolor", () => {
  assert.equal(detectColorMode({ TERM: "xterm-256color" }), "256color");
});

test("detectColorMode: kitty/alacritty/wezterm are treated as truecolor even without COLORTERM", () => {
  assert.equal(detectColorMode({ TERM: "xterm-kitty" }), "truecolor");
  assert.equal(detectColorMode({ TERM: "alacritty" }), "truecolor");
});

test("detectColorMode: a bare color/ansi/xterm TERM falls back to 16color", () => {
  assert.equal(detectColorMode({ TERM: "xterm" }), "16color");
  assert.equal(detectColorMode({ TERM: "ansi" }), "16color");
});

test("detectColorMode: unknown TERM with nothing else set is plain, not a silent 256color guess", () => {
  assert.equal(detectColorMode({ TERM: "vt100" }), "plain");
});

test("styleToAnsi never collapses distinct colors to the same flat fallback in 256color mode", () => {
  const red = styleToAnsi({ fg: "#f38ba8" }, "256color");
  const green = styleToAnsi({ fg: "#a6e3a1" }, "256color");
  assert.notEqual(red.open, green.open, "red and green must produce different SGR codes");
  assert.match(red.open, /\x1b\[38;5;\d+m/);
});

test("styleToAnsi never collapses distinct colors to the same flat fallback in 16color mode", () => {
  const red = styleToAnsi({ fg: "#f38ba8" }, "16color");
  const green = styleToAnsi({ fg: "#a6e3a1" }, "16color");
  assert.notEqual(red.open, green.open, "red and green must map to different ANSI-16 codes");
});

test("styleToAnsi plain mode emits no escape codes at all", () => {
  const result = styleToAnsi({ fg: "#ffffff", bold: true }, "plain");
  assert.equal(result.open, "");
});

test("rgbToAnsi256 maps pure red, green, blue to distinct palette indices", () => {
  const r = rgbToAnsi256(255, 0, 0);
  const g = rgbToAnsi256(0, 255, 0);
  const b = rgbToAnsi256(0, 0, 255);
  assert.notEqual(r, g);
  assert.notEqual(g, b);
  assert.notEqual(r, b);
});

test("rgbToAnsi16 maps black and white to opposite ends of the palette", () => {
  assert.equal(rgbToAnsi16(0, 0, 0), 0);
  assert.equal(rgbToAnsi16(255, 255, 255), 15);
});

test("hexToRgb parses a 6-digit hex color", () => {
  assert.deepEqual(hexToRgb("#ff0080"), [255, 0, 128]);
});

test("computeUsageBar reports the correct tier and textual cue at each threshold", () => {
  assert.equal(computeUsageBar(0, 1000).tier, "ok");
  assert.equal(computeUsageBar(0, 1000).label, "[OK]");
  assert.equal(computeUsageBar(600, 1000).tier, "warn");
  assert.equal(computeUsageBar(850, 1000).tier, "caution");
  assert.equal(computeUsageBar(960, 1000).tier, "critical");
  assert.equal(computeUsageBar(960, 1000).label, "[CRIT]");
});

test("computeUsageBar clamps percent to [0, 100] and handles a zero-size window", () => {
  const overflowing = computeUsageBar(5000, 1000);
  assert.equal(overflowing.percent, 100);
  const noWindow = computeUsageBar(500, 0);
  assert.equal(noWindow.percent, 0);
});

test("tierStyle resolves every tier to a defined theme style", () => {
  for (const tier of ["ok", "warn", "caution", "critical"] as const) {
    assert.ok(tierStyle(tier, DEFAULT_THEME));
  }
});
