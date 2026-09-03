import { spawn, type ChildProcess } from "node:child_process";
import { existsSync, readFileSync, unlinkSync, createWriteStream } from "node:fs";
import { ProductPaths, type ProductLayout } from "../product/paths.js";
import { SocketRuntimeClient } from "../transports/socket.js";
import { CompatibilityNegotiator, type CompatibilityReport } from "../product/compatibility.js";
import type { DaemonStatus } from "@aether/contracts";

export type ManagedRuntimeStatus =
  | "OFFLINE"
  | "STARTING"
  | "RUNNING"
  | "ATTACHED_EXTERNAL"
  | "RECONNECTING"
  | "CRASHED"
  | "STOPPING"
  | "INCOMPATIBLE";

export type ManagedRuntimeEvent =
  | { type: "status_changed"; status: ManagedRuntimeStatus; detail?: string }
  | { type: "compatibility_verified"; report: CompatibilityReport }
  | { type: "log"; text: string; stream: "stdout" | "stderr" }
  | { type: "error"; error: Error };

export type ManagedRuntimeOptions = {
  layout?: ProductLayout;
  pythonExecutable?: string;
  autoRestart?: boolean;
  maxRestarts?: number;
  startupTimeoutMs?: number;
  onEvent?: (event: ManagedRuntimeEvent) => void;
};

export class ManagedRuntimeHost {
  private status: ManagedRuntimeStatus = "OFFLINE";
  private layout: ProductLayout;
  private childProcess: ChildProcess | null = null;
  private isOwned: boolean = false;
  private restartCount: number = 0;
  private readonly options: ManagedRuntimeOptions;
  private readonly listeners: Set<(event: ManagedRuntimeEvent) => void> = new Set();

  constructor(options: ManagedRuntimeOptions = {}) {
    this.options = {
      autoRestart: true,
      maxRestarts: 3,
      startupTimeoutMs: 6000,
      ...options,
    };
    this.layout = options.layout ?? ProductPaths.resolveLayout();
    ProductPaths.ensureUserDirectories(this.layout);
    if (options.onEvent) {
      this.listeners.add(options.onEvent);
    }
  }

  public getStatus(): ManagedRuntimeStatus {
    return this.status;
  }

  public isManaged(): boolean {
    return this.isOwned;
  }

  public getLayout(): ProductLayout {
    return this.layout;
  }

  public subscribe(listener: (event: ManagedRuntimeEvent) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(event: ManagedRuntimeEvent): void {
    for (const l of this.listeners) {
      try {
        l(event);
      } catch {
        /* ignore */
      }
    }
  }

  private setStatus(status: ManagedRuntimeStatus, detail?: string): void {
    if (this.status !== status) {
      this.status = status;
      this.emit({ type: "status_changed", status, detail });
    }
  }

  /**
   * Launch or attach to the AETHER RuntimeService.
   */
  public async ensureRunning(): Promise<{ client: SocketRuntimeClient; report: CompatibilityReport }> {
    // 1. Check if already running / active socket
    const existing = await this.probeExistingDaemon();
    if (existing) {
      this.isOwned = false;
      this.setStatus("ATTACHED_EXTERNAL", "Attached to existing daemon");
      const client = new SocketRuntimeClient({ socketPath: this.layout.socketPath });
      const statusRes = await client.getDaemonStatus();
      const report = CompatibilityNegotiator.evaluate(statusRes.ok ? statusRes.value : null);
      this.emit({ type: "compatibility_verified", report });
      if (report.status === "INCOMPATIBLE") {
        this.setStatus("INCOMPATIBLE", report.reasons.join("; "));
      } else {
        this.setStatus("RUNNING");
      }
      return { client, report };
    }

    // 2. Clean stale PID file if present
    this.cleanStalePid();

    // 3. Spawn managed runtime
    this.setStatus("STARTING", "Spawning AETHER backend runtime...");
    await this.spawnRuntimeProcess();

    // 4. Poll socket for readiness
    const client = new SocketRuntimeClient({ socketPath: this.layout.socketPath });
    const daemonStatus = await this.waitForReadiness(client);

    // 5. Negotiate compatibility
    const report = CompatibilityNegotiator.evaluate(daemonStatus);
    this.emit({ type: "compatibility_verified", report });

    if (report.status === "INCOMPATIBLE") {
      this.setStatus("INCOMPATIBLE", report.reasons.join("; "));
      throw new Error(`Incompatible runtime: ${report.reasons.join("; ")}`);
    }

    this.setStatus("RUNNING", "Managed runtime online");
    this.restartCount = 0;
    return { client, report };
  }

  private async probeExistingDaemon(): Promise<boolean> {
    if (!existsSync(this.layout.socketPath)) {
      return false;
    }
    const client = new SocketRuntimeClient({ socketPath: this.layout.socketPath });
    try {
      const res = await Promise.race([
        client.getDaemonStatus(),
        new Promise<never>((_, reject) => setTimeout(() => reject(new Error("Probe timeout")), 800)),
      ]);
      return res.ok;
    } catch {
      return false;
    }
  }

  private cleanStalePid(): void {
    if (existsSync(this.layout.pidFile)) {
      try {
        const raw = readFileSync(this.layout.pidFile, "utf-8").trim();
        const pid = parseInt(raw, 10);
        if (!Number.isNaN(pid) && pid > 0) {
          try {
            process.kill(pid, 0); // Check if alive
          } catch {
            // Dead process, unlink PID file
            unlinkSync(this.layout.pidFile);
          }
        }
      } catch {
        /* ignore */
      }
    }
  }

  private async spawnRuntimeProcess(): Promise<void> {
    const python = this.options.pythonExecutable ?? process.env.PYTHON_BIN ?? "python3";
    const entrypoint = this.layout.runtimeEntrypoint;

    // Log routing
    const logFile = `${this.layout.logsDir}/runtime.log`;
    const logStream = createWriteStream(logFile, { flags: "a" });

    const args = [
      "-u", // unbuffered stdio
      entrypoint,
      // vanguard/packages/runtime/standalone_daemon.py's real argparse flag
      // is `--socket`, not `--socket-path` -- verified against its source.
      "--socket",
      this.layout.socketPath,
      "--state-dir",
      this.layout.stateDir,
      "--data-dir",
      this.layout.dataDir,
      "--pid-file",
      this.layout.pidFile,
      "--json",
    ];

    const env = {
      ...process.env,
      PYTHONPATH: `${this.layout.runtimeDir}${process.platform === "win32" ? ";" : ":"}${process.env.PYTHONPATH ?? ""}`,
      VANGUARD_ROOT: this.layout.appRoot,
    };

    const child = spawn(python, args, {
      env,
      stdio: ["ignore", "pipe", "pipe"],
      detached: false,
    });

    this.childProcess = child;
    this.isOwned = true;

    child.stdout?.on("data", (chunk: Buffer) => {
      const text = chunk.toString();
      logStream.write(`[OUT] ${text}`);
      this.emit({ type: "log", text, stream: "stdout" });
    });

    child.stderr?.on("data", (chunk: Buffer) => {
      const text = chunk.toString();
      logStream.write(`[ERR] ${text}`);
      this.emit({ type: "log", text, stream: "stderr" });
    });

    child.on("error", (err) => {
      this.emit({ type: "error", error: err });
    });

    child.on("exit", (code, sig) => {
      logStream.write(`[EXIT] Runtime exited with code ${code}, signal ${sig}\n`);
      if (this.status !== "STOPPING" && this.status !== "OFFLINE") {
        this.setStatus("CRASHED", `Runtime exited unexpectedly (${code ?? sig})`);
        this.handleUnexpectedCrash();
      }
      this.childProcess = null;
    });
  }

  private async waitForReadiness(client: SocketRuntimeClient): Promise<DaemonStatus> {
    const timeout = this.options.startupTimeoutMs ?? 6000;
    const start = Date.now();

    while (Date.now() - start < timeout) {
      if (existsSync(this.layout.socketPath)) {
        try {
          const res = await client.getDaemonStatus();
          if (res.ok) {
            return res.value;
          }
        } catch {
          /* wait and retry */
        }
      }
      await new Promise((resolve) => setTimeout(resolve, 200));
    }

    throw new Error(`Managed runtime failed to initialize within ${timeout}ms at ${this.layout.socketPath}`);
  }

  private handleUnexpectedCrash(): void {
    if (!this.options.autoRestart) return;

    if (this.restartCount < (this.options.maxRestarts ?? 3)) {
      this.restartCount++;
      const backoff = Math.min(1000 * Math.pow(2, this.restartCount - 1), 5000);
      this.setStatus("RECONNECTING", `Restarting runtime in ${backoff}ms (attempt ${this.restartCount})...`);

      setTimeout(() => {
        this.ensureRunning().catch((err) => {
          this.emit({ type: "error", error: err });
        });
      }, backoff);
    }
  }

  /**
   * Graceful shutdown of managed runtime.
   */
  public async shutdown(): Promise<void> {
    if (!this.isOwned || !this.childProcess) {
      this.setStatus("OFFLINE");
      return;
    }

    this.setStatus("STOPPING", "Stopping managed runtime...");
    const child = this.childProcess;
    this.childProcess = null;

    return new Promise<void>((resolve) => {
      const timer = setTimeout(() => {
        try {
          child.kill("SIGKILL");
        } catch {
          /* ignore */
        }
        this.setStatus("OFFLINE");
        resolve();
      }, 2000);

      child.once("exit", () => {
        clearTimeout(timer);
        this.setStatus("OFFLINE");
        resolve();
      });

      try {
        child.kill("SIGTERM");
      } catch {
        clearTimeout(timer);
        this.setStatus("OFFLINE");
        resolve();
      }
    });
  }
}
