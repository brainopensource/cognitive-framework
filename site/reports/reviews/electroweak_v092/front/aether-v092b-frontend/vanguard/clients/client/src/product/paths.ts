import { homedir, platform } from "node:os";
import { resolve, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { existsSync, mkdirSync } from "node:fs";

export type ProductPlatform = "linux" | "darwin" | "win32";

export type ProductLayout = {
  // Immutable Application Assets
  appRoot: string;
  binDir: string;
  runtimeDir: string;
  runtimeEntrypoint: string;
  schemasDir: string;
  labDir: string;

  // Mutable User Data (Platform-appropriate)
  configDir: string;
  configFile: string;
  credentialsFile: string;
  stateDir: string;
  dataDir: string;
  socketPath: string;
  pidFile: string;
  logsDir: string;
  cacheDir: string;
};

export class ProductPaths {
  private static cachedLayout?: ProductLayout;

  public static getPlatform(): ProductPlatform {
    const p = platform();
    if (p === "win32" || p === "darwin") return p;
    return "linux";
  }

  public static resolveLayout(customAppRoot?: string): ProductLayout {
    if (this.cachedLayout && !customAppRoot) {
      return this.cachedLayout;
    }

    const currentPlatform = this.getPlatform();
    const home = homedir();

    let fallbackRoot = process.cwd();
    try {
      if (typeof import.meta !== "undefined" && import.meta.url) {
        const currentFile = fileURLToPath(import.meta.url);
        fallbackRoot = resolve(dirname(currentFile), "../../../..");
      }
    } catch {
      fallbackRoot = process.cwd();
    }

    // 1. Immutable App Root Resolution
    // Precedence: AETHER_HOME env -> customAppRoot -> process.resourcesPath (Tauri) -> package root
    const appRoot =
      process.env.AETHER_HOME ??
      customAppRoot ??
      (process as any).resourcesPath ??
      fallbackRoot;

    const binDir = join(appRoot, "bin");
    const runtimeDir = join(appRoot, "vanguard", "packages");
    const runtimeEntrypoint = join(appRoot, "vanguard", "packages", "runtime", "standalone_daemon.py");
    const schemasDir = join(appRoot, "schemas");
    const labDir = join(appRoot, "vanguard", "clients", "lab", "dist");

    // 2. Mutable User Directories
    let configDir: string;
    let stateDir: string;
    let dataDir: string;
    let socketPath: string;
    let logsDir: string;
    let cacheDir: string;

    if (currentPlatform === "win32") {
      const appData = process.env.APPDATA ?? join(home, "AppData", "Roaming");
      const localAppData = process.env.LOCALAPPDATA ?? join(home, "AppData", "Local");
      configDir = join(appData, "Aether");
      stateDir = join(localAppData, "Aether", "state");
      dataDir = join(localAppData, "Aether", "data");
      socketPath = join(stateDir, "runtime.sock");
      logsDir = join(localAppData, "Aether", "logs");
      cacheDir = join(localAppData, "Aether", "cache");
    } else if (currentPlatform === "darwin") {
      configDir = join(home, "Library", "Application Support", "Aether");
      stateDir = join(home, "Library", "Application Support", "Aether", "state");
      dataDir = join(home, "Library", "Application Support", "Aether", "data");
      socketPath = join(stateDir, "runtime.sock");
      logsDir = join(home, "Library", "Logs", "Aether");
      cacheDir = join(home, "Library", "Caches", "Aether");
    } else {
      // Linux / XDG
      const xdgConfig = process.env.XDG_CONFIG_HOME ?? join(home, ".config");
      const xdgData = process.env.XDG_DATA_HOME ?? join(home, ".local", "share");
      const xdgState = process.env.XDG_STATE_HOME ?? join(home, ".local", "state");
      const xdgCache = process.env.XDG_CACHE_HOME ?? join(home, ".cache");

      configDir = join(xdgConfig, "aether");
      stateDir = join(xdgState, "aether");
      dataDir = join(xdgData, "aether");
      socketPath = process.env.AETHER_RUNTIME_SOCK ?? "/tmp/vanguard-runtime.sock";
      logsDir = join(stateDir, "logs");
      cacheDir = join(xdgCache, "aether");
    }

    const configFile = join(configDir, "config.json");
    const credentialsFile = join(configDir, "credentials.json");
    const pidFile = join(stateDir, "runtime.pid");

    const layout: ProductLayout = {
      appRoot,
      binDir,
      runtimeDir,
      runtimeEntrypoint,
      schemasDir,
      labDir,
      configDir,
      configFile,
      credentialsFile,
      stateDir,
      dataDir,
      socketPath,
      pidFile,
      logsDir,
      cacheDir,
    };

    if (!customAppRoot) {
      this.cachedLayout = layout;
    }

    return layout;
  }

  public static ensureUserDirectories(layout?: ProductLayout): void {
    const l = layout ?? this.resolveLayout();
    for (const dir of [l.configDir, l.stateDir, l.dataDir, l.logsDir, l.cacheDir]) {
      if (!existsSync(dir)) {
        try {
          mkdirSync(dir, { recursive: true, mode: 0o700 });
        } catch {
          /* ignore */
        }
      }
    }
  }
}
