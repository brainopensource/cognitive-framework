import type {
  FrontendSettings,
  ModelProviderConfig,
  FrontendConversationMeta,
  CredentialState,
} from "@aether/contracts";

export interface FrontendPersistencePort {
  loadSettings(): Promise<Partial<FrontendSettings> | null>;
  saveSettings(settings: FrontendSettings): Promise<void>;

  loadProviders(): Promise<ModelProviderConfig[] | null>;
  saveProviders(providers: ModelProviderConfig[]): Promise<void>;

  loadConversations(): Promise<FrontendConversationMeta[] | null>;
  saveConversations(conversations: FrontendConversationMeta[]): Promise<void>;

  loadDraft(conversationId: string): Promise<string | null>;
  saveDraft(conversationId: string, draft: string): Promise<void>;

  loadRecentWorkspaces(): Promise<string[] | null>;
  saveRecentWorkspaces(workspaces: string[]): Promise<void>;

  getCredentialState(keyRef: string): Promise<CredentialState>;
  saveSecureCredential(keyRef: string, secret: string): Promise<void>;
  deleteSecureCredential(keyRef: string): Promise<void>;
}

export class InMemoryPersistenceAdapter implements FrontendPersistencePort {
  private settings: FrontendSettings | null = null;
  private providers: ModelProviderConfig[] | null = null;
  private conversations: FrontendConversationMeta[] | null = null;
  private drafts = new Map<string, string>();
  private recents: string[] | null = null;
  private credentials = new Map<string, string>();

  async loadSettings(): Promise<Partial<FrontendSettings> | null> {
    return this.settings;
  }
  async saveSettings(settings: FrontendSettings): Promise<void> {
    this.settings = JSON.parse(JSON.stringify(settings));
  }

  async loadProviders(): Promise<ModelProviderConfig[] | null> {
    return this.providers ? JSON.parse(JSON.stringify(this.providers)) : null;
  }
  async saveProviders(providers: ModelProviderConfig[]): Promise<void> {
    this.providers = JSON.parse(JSON.stringify(providers));
  }

  async loadConversations(): Promise<FrontendConversationMeta[] | null> {
    return this.conversations ? JSON.parse(JSON.stringify(this.conversations)) : null;
  }
  async saveConversations(conversations: FrontendConversationMeta[]): Promise<void> {
    this.conversations = JSON.parse(JSON.stringify(conversations));
  }

  async loadDraft(conversationId: string): Promise<string | null> {
    return this.drafts.get(conversationId) ?? null;
  }
  async saveDraft(conversationId: string, draft: string): Promise<void> {
    this.drafts.set(conversationId, draft);
  }

  async loadRecentWorkspaces(): Promise<string[] | null> {
    return this.recents ? [...this.recents] : null;
  }
  async saveRecentWorkspaces(workspaces: string[]): Promise<void> {
    this.recents = [...workspaces];
  }

  async getCredentialState(keyRef: string): Promise<CredentialState> {
    const val = this.credentials.get(keyRef);
    if (!val) return "NOT_CONFIGURED";
    return val.length >= 4 ? "CONFIGURED" : "INVALID";
  }
  async saveSecureCredential(keyRef: string, secret: string): Promise<void> {
    this.credentials.set(keyRef, secret);
  }
  async deleteSecureCredential(keyRef: string): Promise<void> {
    this.credentials.delete(keyRef);
  }
}

export class LocalStoragePersistenceAdapter implements FrontendPersistencePort {
  private memoryFallback = new InMemoryPersistenceAdapter();

  private isAvailable(): boolean {
    return typeof globalThis !== "undefined" && typeof (globalThis as any).localStorage !== "undefined";
  }

  async loadSettings(): Promise<Partial<FrontendSettings> | null> {
    if (!this.isAvailable()) return this.memoryFallback.loadSettings();
    try {
      const raw = localStorage.getItem("aether:settings");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return this.memoryFallback.loadSettings();
    }
  }

  async saveSettings(settings: FrontendSettings): Promise<void> {
    if (!this.isAvailable()) return this.memoryFallback.saveSettings(settings);
    try {
      localStorage.setItem("aether:settings", JSON.stringify(settings));
    } catch {
      await this.memoryFallback.saveSettings(settings);
    }
  }

  async loadProviders(): Promise<ModelProviderConfig[] | null> {
    if (!this.isAvailable()) return this.memoryFallback.loadProviders();
    try {
      const raw = localStorage.getItem("aether:providers");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return this.memoryFallback.loadProviders();
    }
  }

  async saveProviders(providers: ModelProviderConfig[]): Promise<void> {
    // Strip any raw secrets before saving to ordinary settings storage
    const safeProviders = providers.map((p) => {
      const { ...safe } = p;
      return safe;
    });
    if (!this.isAvailable()) return this.memoryFallback.saveProviders(safeProviders);
    try {
      localStorage.setItem("aether:providers", JSON.stringify(safeProviders));
    } catch {
      await this.memoryFallback.saveProviders(safeProviders);
    }
  }

  async loadConversations(): Promise<FrontendConversationMeta[] | null> {
    if (!this.isAvailable()) return this.memoryFallback.loadConversations();
    try {
      const raw = localStorage.getItem("aether:conversations");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return this.memoryFallback.loadConversations();
    }
  }

  async saveConversations(conversations: FrontendConversationMeta[]): Promise<void> {
    if (!this.isAvailable()) return this.memoryFallback.saveConversations(conversations);
    try {
      localStorage.setItem("aether:conversations", JSON.stringify(conversations));
    } catch {
      await this.memoryFallback.saveConversations(conversations);
    }
  }

  async loadDraft(conversationId: string): Promise<string | null> {
    if (!this.isAvailable()) return this.memoryFallback.loadDraft(conversationId);
    try {
      return localStorage.getItem(`aether:draft:${conversationId}`);
    } catch {
      return this.memoryFallback.loadDraft(conversationId);
    }
  }

  async saveDraft(conversationId: string, draft: string): Promise<void> {
    if (!this.isAvailable()) return this.memoryFallback.saveDraft(conversationId, draft);
    try {
      localStorage.setItem(`aether:draft:${conversationId}`, draft);
    } catch {
      await this.memoryFallback.saveDraft(conversationId, draft);
    }
  }

  async loadRecentWorkspaces(): Promise<string[] | null> {
    if (!this.isAvailable()) return this.memoryFallback.loadRecentWorkspaces();
    try {
      const raw = localStorage.getItem("aether:recent_workspaces");
      return raw ? JSON.parse(raw) : null;
    } catch {
      return this.memoryFallback.loadRecentWorkspaces();
    }
  }

  async saveRecentWorkspaces(workspaces: string[]): Promise<void> {
    if (!this.isAvailable()) return this.memoryFallback.saveRecentWorkspaces(workspaces);
    try {
      localStorage.setItem("aether:recent_workspaces", JSON.stringify(workspaces));
    } catch {
      await this.memoryFallback.saveRecentWorkspaces(workspaces);
    }
  }

  async getCredentialState(keyRef: string): Promise<CredentialState> {
    // Delegated to memory/session or secure vault, never stored in plaintext localStorage
    return this.memoryFallback.getCredentialState(keyRef);
  }

  async saveSecureCredential(keyRef: string, secret: string): Promise<void> {
    return this.memoryFallback.saveSecureCredential(keyRef, secret);
  }

  async deleteSecureCredential(keyRef: string): Promise<void> {
    return this.memoryFallback.deleteSecureCredential(keyRef);
  }
}

export class NodeFsPersistenceAdapter implements FrontendPersistencePort {
  private memoryFallback = new InMemoryPersistenceAdapter();
  private baseDir: string;

  constructor(customBaseDir?: string) {
    if (customBaseDir) {
      this.baseDir = customBaseDir;
    } else if (typeof process !== "undefined" && process.env) {
      const xdgConfig = process.env.XDG_CONFIG_HOME;
      const home = process.env.HOME || process.env.USERPROFILE || "/tmp";
      this.baseDir = xdgConfig ? `${xdgConfig}/aether` : `${home}/.config/aether`;
    } else {
      this.baseDir = "/tmp/.aether";
    }
  }

  private isNode(): boolean {
    return typeof process !== "undefined" && Boolean(process.versions?.node);
  }

  private async ensureDir(): Promise<void> {
    if (!this.isNode()) return;
    try {
      const fs = await import("node:fs");
      if (!fs.existsSync(this.baseDir)) {
        fs.mkdirSync(this.baseDir, { recursive: true, mode: 0o700 });
      }
    } catch {
      /* ignore */
    }
  }

  private async readJson<T>(filename: string): Promise<T | null> {
    if (!this.isNode()) return null;
    try {
      const fs = await import("node:fs");
      const filePath = `${this.baseDir}/${filename}`;
      if (!fs.existsSync(filePath)) return null;
      const raw = fs.readFileSync(filePath, "utf-8");
      return JSON.parse(raw) as T;
    } catch {
      return null;
    }
  }

  private async writeJson<T>(filename: string, data: T, mode: number = 0o600): Promise<void> {
    if (!this.isNode()) return;
    try {
      await this.ensureDir();
      const fs = await import("node:fs");
      const filePath = `${this.baseDir}/${filename}`;
      fs.writeFileSync(filePath, JSON.stringify(data, null, 2), { encoding: "utf-8", mode });
    } catch {
      /* ignore */
    }
  }

  async loadSettings(): Promise<Partial<FrontendSettings> | null> {
    const data =
      (await this.readJson<Partial<FrontendSettings>>("config.json")) ??
      (await this.readJson<Partial<FrontendSettings>>("settings.json"));
    return data ?? this.memoryFallback.loadSettings();
  }

  async saveSettings(settings: FrontendSettings): Promise<void> {
    await this.writeJson("settings.json", settings);
    await this.memoryFallback.saveSettings(settings);
  }

  async loadProviders(): Promise<ModelProviderConfig[] | null> {
    const data = await this.readJson<ModelProviderConfig[]>("providers.json");
    return data ?? this.memoryFallback.loadProviders();
  }

  async saveProviders(providers: ModelProviderConfig[]): Promise<void> {
    await this.writeJson("providers.json", providers);
    await this.memoryFallback.saveProviders(providers);
  }

  async loadConversations(): Promise<FrontendConversationMeta[] | null> {
    const data = await this.readJson<FrontendConversationMeta[]>("conversations.json");
    return data ?? this.memoryFallback.loadConversations();
  }

  async saveConversations(conversations: FrontendConversationMeta[]): Promise<void> {
    await this.writeJson("conversations.json", conversations);
    await this.memoryFallback.saveConversations(conversations);
  }

  async loadDraft(conversationId: string): Promise<string | null> {
    const drafts = await this.readJson<Record<string, string>>("drafts.json");
    return drafts?.[conversationId] ?? this.memoryFallback.loadDraft(conversationId);
  }

  async saveDraft(conversationId: string, draft: string): Promise<void> {
    const drafts = (await this.readJson<Record<string, string>>("drafts.json")) ?? {};
    drafts[conversationId] = draft;
    await this.writeJson("drafts.json", drafts);
    await this.memoryFallback.saveDraft(conversationId, draft);
  }

  async loadRecentWorkspaces(): Promise<string[] | null> {
    const data = await this.readJson<string[]>("workspaces.json");
    return data ?? this.memoryFallback.loadRecentWorkspaces();
  }

  async saveRecentWorkspaces(workspaces: string[]): Promise<void> {
    await this.writeJson("workspaces.json", workspaces);
    await this.memoryFallback.saveRecentWorkspaces(workspaces);
  }

  async getCredentialState(keyRef: string): Promise<CredentialState> {
    const creds = await this.readJson<Record<string, string>>("credentials.json");
    if (creds && creds[keyRef]) {
      return creds[keyRef].length >= 4 ? "CONFIGURED" : "INVALID";
    }
    return this.memoryFallback.getCredentialState(keyRef);
  }

  async saveSecureCredential(keyRef: string, secret: string): Promise<void> {
    const creds = (await this.readJson<Record<string, string>>("credentials.json")) ?? {};
    creds[keyRef] = secret;
    await this.writeJson("credentials.json", creds, 0o600);
    await this.memoryFallback.saveSecureCredential(keyRef, secret);
  }

  async deleteSecureCredential(keyRef: string): Promise<void> {
    const creds = await this.readJson<Record<string, string>>("credentials.json");
    if (creds) {
      delete creds[keyRef];
      await this.writeJson("credentials.json", creds, 0o600);
    }
    await this.memoryFallback.deleteSecureCredential(keyRef);
  }
}

