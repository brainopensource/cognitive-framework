/**
 * Credential status and provider reachability, answered by the gateway.
 *
 * The Settings pane used to render a provider list whose `credentialState`
 * came from browser-side defaults, so it displayed "CONFIGURED" and a masked
 * placeholder on a machine with no key at all. Nothing in the page can know
 * whether the runtime can load a secret -- only the runtime can -- so both
 * questions are asked over the wire, and the secret itself never travels.
 */

export type CredentialState =
  | "CONFIGURED"
  | "MISSING"
  | "DENIED"
  | "INVALID"
  | "EXHAUSTED"
  | "RATE_LIMITED"
  | "UNREACHABLE"
  | "UNKNOWN";

export type CredentialStatus = {
  keyRef: string;
  state: CredentialState;
  source: string;
  detail: string;
  remedy: string;
};

export type ProviderProbeResult = CredentialStatus & {
  ok: boolean;
  model: string;
};

const UNKNOWN: CredentialStatus = {
  keyRef: "OPENROUTER_API_KEY",
  state: "UNKNOWN",
  source: "",
  detail: "the gateway did not answer the credential query",
  remedy: "Confirm the runtime gateway is running, then retry.",
};

function asStatus(raw: unknown, fallback: CredentialStatus): CredentialStatus {
  if (!raw || typeof raw !== "object") return fallback;
  const row = raw as Record<string, unknown>;
  return {
    keyRef: String(row.keyRef ?? fallback.keyRef),
    state: (row.state as CredentialState) ?? fallback.state,
    source: String(row.source ?? ""),
    detail: String(row.detail ?? fallback.detail),
    remedy: String(row.remedy ?? ""),
  };
}

export async function fetchCredentialStatus(baseUrl: string): Promise<CredentialStatus> {
  try {
    const response = await fetch(`${baseUrl}/api/credentials`, { cache: "no-store" });
    if (!response.ok) {
      return { ...UNKNOWN, detail: `gateway returned HTTP ${response.status}` };
    }
    return asStatus(await response.json(), UNKNOWN);
  } catch (error) {
    return { ...UNKNOWN, detail: `could not reach the gateway: ${String(error)}` };
  }
}

/**
 * Spend one token against the provider and report the outcome.
 *
 * This is what "Test Connection" now does. Previously it re-read local state
 * and updated nothing an operator could see, which is indistinguishable from
 * a button that does nothing.
 */
export async function probeProvider(
  baseUrl: string,
  model?: string,
): Promise<ProviderProbeResult> {
  const failure = (detail: string): ProviderProbeResult => ({
    ...UNKNOWN,
    ok: false,
    model: model ?? "",
    detail,
  });
  try {
    const response = await fetch(`${baseUrl}/api/credentials:test`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(model ? { model } : {}),
    });
    const raw = (await response.json()) as Record<string, unknown>;
    return {
      ...asStatus(raw, UNKNOWN),
      ok: Boolean(raw.ok),
      model: String(raw.model ?? model ?? ""),
    };
  } catch (error) {
    return failure(`could not reach the gateway: ${String(error)}`);
  }
}
