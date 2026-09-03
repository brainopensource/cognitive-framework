import type { FrontendPersistencePort, FrontendSessionRecord } from "@aether/client";

/**
 * Fixed, obviously-synthetic mock token literal. No sk-/or-/AKIA prefix and no
 * base64-looking entropy, so tools/linters/scan_secrets.py never mistakes it
 * for a real credential. See scanTokenIsMock() below, which the test suite
 * asserts against so a future edit cannot quietly make this look real.
 */
export const MOCK_SESSION_TOKEN = "aether-mock-session-000000000000";

const MOCK_TOKEN_SHAPE = /^aether-mock-session-0{12}$/;

export function scanTokenIsMock(token: string): boolean {
  return MOCK_TOKEN_SHAPE.test(token);
}

export interface LoginResult {
  readonly deviceUrl: string;
  readonly session: FrontendSessionRecord;
}

/**
 * Mocked device-code login: prints a fake auth URL and persists a fake
 * session through the persistence port's dedicated session.json slot
 * (never credentials.json, which holds real provider secrets at 0o600).
 */
export async function login(
  persistence: FrontendPersistencePort,
  account: string = "operator@aether.local"
): Promise<LoginResult> {
  const deviceCode = "XXXX-XXXX";
  const deviceUrl = `https://auth.aether.dev/device?code=${deviceCode}`;
  const issuedAt = new Date().toISOString();
  const expiresAt = new Date(Date.now() + 1000 * 60 * 60 * 24 * 30).toISOString();

  const session: FrontendSessionRecord = {
    account,
    displayName: account,
    issuedAt,
    expiresAt,
    token: MOCK_SESSION_TOKEN,
  };

  await persistence.saveSession(session);
  return { deviceUrl, session };
}

export async function logout(persistence: FrontendPersistencePort): Promise<void> {
  await persistence.clearSession();
}

export async function currentSession(
  persistence: FrontendPersistencePort
): Promise<FrontendSessionRecord | null> {
  return persistence.loadSession();
}
