import type { DaemonStatus } from "@aether/contracts";

export type CompatibilityStatus = "COMPATIBLE" | "DEGRADED" | "INCOMPATIBLE";

export type CompatibilityReport = {
  status: CompatibilityStatus;
  frontendVersion: string;
  runtimeVersion?: string;
  expectedProtocol: string;
  actualProtocol?: string;
  reasons: string[];
  capabilities: string[];
};

export const CURRENT_FRONTEND_VERSION = "0.9.0b1";
export const EXPECTED_WIRE_PROTOCOL = "vg.4";

export class CompatibilityNegotiator {
  public static evaluate(
    status: DaemonStatus | null,
    frontendVersion: string = CURRENT_FRONTEND_VERSION,
    expectedProtocol: string = EXPECTED_WIRE_PROTOCOL
  ): CompatibilityReport {
    const reasons: string[] = [];
    const rawAny = (status as any) ?? {};
    const capabilities: string[] = rawAny.capabilities ?? ["StartRun", "GetRun", "StreamEvents"];

    if (!status || status.status !== "running") {
      return {
        status: "INCOMPATIBLE",
        frontendVersion,
        expectedProtocol,
        reasons: ["Daemon status unavailable or daemon offline"],
        capabilities: [],
      };
    }

    const actualProtocol = rawAny.protocol ?? "vg.4";
    const runtimeVersion = status.version ?? "0.9.0b1";

    // 1. Check Wire Protocol Compatibility
    if (actualProtocol !== expectedProtocol) {
      reasons.push(
        `Wire protocol mismatch: frontend expects '${expectedProtocol}', runtime uses '${actualProtocol}'`
      );
      return {
        status: "INCOMPATIBLE",
        frontendVersion,
        runtimeVersion,
        expectedProtocol,
        actualProtocol,
        reasons,
        capabilities,
      };
    }

    // 2. Check Major Version
    const frontMajor = frontendVersion.split(".")[0];
    const runMajor = runtimeVersion.split(".")[0];
    if (frontMajor !== runMajor) {
      reasons.push(
        `Major version mismatch: frontend version is '${frontendVersion}', runtime is '${runtimeVersion}'`
      );
      return {
        status: "INCOMPATIBLE",
        frontendVersion,
        runtimeVersion,
        expectedProtocol,
        actualProtocol,
        reasons,
        capabilities,
      };
    }

    // 3. Check Required Capabilities
    const requiredCaps = ["StartRun", "StreamEvents"];
    const missingCaps = requiredCaps.filter((c) => !capabilities.includes(c));
    if (missingCaps.length > 0) {
      reasons.push(`Runtime is missing required capabilities: ${missingCaps.join(", ")}`);
      return {
        status: "INCOMPATIBLE",
        frontendVersion,
        runtimeVersion,
        expectedProtocol,
        actualProtocol,
        reasons,
        capabilities,
      };
    }

    return {
      status: "COMPATIBLE",
      frontendVersion,
      runtimeVersion,
      expectedProtocol,
      actualProtocol,
      reasons: [],
      capabilities,
    };
  }
}
