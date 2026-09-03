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

const DAEMON_RELATIVE = join("vanguard", "packages", "runtime", "standalone_daemon.py");

function hasDaemon(root: string): boolean {
  return existsSync(join(root, DAEMON_RELATIVE));
}

function walkToAppRoot(seed: string): string | undefined {
  let dir = resolve(seed);
  for (let i = 0; i < 24; i++) {
    if (hasDaemon(dir)) return dir;
    const parent = dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return undefined;
}

export class ProductPaths {
  private static cachedLayout?: ProductLayout;

  public static clearCache(): void {
    this.cachedLayout = undefined;
  }

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

    let moduleDir = process.cwd();
    try {
      if (typeof import.meta !== "undefined" && import.meta.url) {
        moduleDir = dirname(fileURLToPath(import.meta.url));
      }
    } catch {
      moduleDir = process.cwd();
    }

    const envHome = process.env.AETHER_HOME;
    const envRoot = envHome && hasDaemon(envHome) ? envHome : undefined;
    const custom = customAppRoot && hasDaemon(customAppRoot) ? customAppRoot : customAppRoot;
    const walked = walkToAppRoot(moduleDir) ?? walkToAppRoot(process.cwd());

    const appRoot = envRoot ?? custom ?? walked ?? process.cwd();

    const binDir = join(appRoot, "bin");
    const runtimeDir = join(appRoot, "vanguard", "packages");
    const runtimeEntrypoint = join(appRoot, DAEMON_RELATIVE);
    const schemasDir = join(appRoot, "schemas");
    const labDir = join(appRoot, "vanguard", "clients", "lab", "dist");

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
