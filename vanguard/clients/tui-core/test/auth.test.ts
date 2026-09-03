import test from "node:test";
import assert from "node:assert/strict";
import { InMemoryPersistenceAdapter } from "@aether/client";
import { login, logout, currentSession, MOCK_SESSION_TOKEN, scanTokenIsMock } from "../src/auth/session.js";

test("MOCK_SESSION_TOKEN is unmistakably synthetic (no sk-/or-/AKIA prefix, no PEM, no real-looking entropy)", () => {
  assert.equal(scanTokenIsMock(MOCK_SESSION_TOKEN), true);
  assert.doesNotMatch(MOCK_SESSION_TOKEN, /^sk-/);
  assert.doesNotMatch(MOCK_SESSION_TOKEN, /^or-/);
  assert.doesNotMatch(MOCK_SESSION_TOKEN, /^AKIA[0-9A-Z]{16}$/);
  assert.doesNotMatch(MOCK_SESSION_TOKEN, /BEGIN [A-Z ]*PRIVATE KEY/);
});

test("login persists a session record through the persistence port, logout clears it", async () => {
  const persistence = new InMemoryPersistenceAdapter();

  assert.equal(await currentSession(persistence), null);

  const result = await login(persistence, "someone@example.com");
  assert.equal(result.session.account, "someone@example.com");
  assert.equal(result.session.token, MOCK_SESSION_TOKEN);
  assert.match(result.deviceUrl, /^https:\/\/auth\.aether\.dev\/device\?code=/);

  const stored = await currentSession(persistence);
  assert.deepEqual(stored, result.session);

  await logout(persistence);
  assert.equal(await currentSession(persistence), null);
});
