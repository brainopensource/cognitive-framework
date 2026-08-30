import type { ParsedCli } from "../composition/parse-cli.js";
import { NodeFsPersistenceAdapter, DEFAULT_PROVIDERS } from "@aether/client";
import type { ModelProviderConfig, ProviderType } from "@aether/contracts";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleProvider(args: string[], options: ParsedCli): Promise<number> {
  const persistence = new NodeFsPersistenceAdapter();
  const subcommand = args[0] || "list";

  let providers: ModelProviderConfig[] = (await persistence.loadProviders()) ?? [];
  if (providers.length === 0) {
    providers = DEFAULT_PROVIDERS;
    await persistence.saveProviders(providers);
  }

  if (subcommand === "list") {
    // Populate credential status for each provider
    const enriched = await Promise.all(
      providers.map(async (p: ModelProviderConfig) => {
        let credState = "NOT_CONFIGURED";
        if (p.credentialKeyRef) {
          credState = await persistence.getCredentialState(p.credentialKeyRef);
        }
        return {
          id: p.id,
          name: p.name,
          type: p.type,
          isDefault: Boolean(p.isDefault),
          selectedModel: p.selectedModel,
          modelCount: p.models.length,
          credentialStatus:
            credState === "CONFIGURED"
              ? "READY"
              : credState === "INVALID"
              ? "INVALID"
              : "MISSING CREDENTIAL",
        };
      })
    );

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "provider list",
        status: "success",
        data: { providers: enriched },
      });
    } else {
      console.log(`\nConfigured Model Providers (${enriched.length}):`);
      console.log(`  ${"ID".padEnd(20)} ${"NAME".padEnd(20)} ${"TYPE".padEnd(14)} ${"STATUS".padEnd(20)} ${"MODEL"}`);
      console.log(`  ${"-".repeat(80)}`);
      for (const p of enriched) {
        const defTag = p.isDefault ? " (default)" : "";
        console.log(
          `  ${(p.id + defTag).padEnd(20)} ${p.name.padEnd(20)} ${p.type.padEnd(14)} ${p.credentialStatus.padEnd(20)} ${p.selectedModel}`
        );
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "inspect" || subcommand === "show") {
    const id = args[1];
    if (!id) {
      logDiagnostic("Missing <provider-id> for provider inspect");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }
    const match = providers.find((p: ModelProviderConfig) => p.id === id);
    if (!match) {
      logDiagnostic(`Provider '${id}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const credState = match.credentialKeyRef ? await persistence.getCredentialState(match.credentialKeyRef) : "NOT_CONFIGURED";
    const status = credState === "CONFIGURED" ? "READY" : credState === "INVALID" ? "INVALID" : "MISSING CREDENTIAL";

    const detail = {
      id: match.id,
      name: match.name,
      type: match.type,
      baseUrl: match.baseUrl,
      isDefault: Boolean(match.isDefault),
      selectedModel: match.selectedModel,
      credentialKeyRef: match.credentialKeyRef,
      credentialStatus: status,
      models: match.models,
    };

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "provider inspect",
        status: "success",
        data: detail,
      });
    } else {
      console.log(`\nProvider: ${match.name} (${match.id})${match.isDefault ? " [DEFAULT]" : ""}`);
      console.log(`  Type:              ${match.type}`);
      if (match.baseUrl) console.log(`  Base URL:          ${match.baseUrl}`);
      console.log(`  Credential Status: ${status}`);
      console.log(`  Selected Model:    ${match.selectedModel}`);
      console.log(`  Available Models (${match.models.length}):`);
      for (const m of match.models) {
        console.log(`    - ${m.id} (${m.name})`);
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "default") {
    const id = args[1];
    if (!id) {
      const currentDefault = providers.find((p: ModelProviderConfig) => p.isDefault) ?? providers[0];
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "provider default",
          status: "success",
          data: { defaultProviderId: currentDefault?.id },
        });
      } else {
        console.log(`Current default provider: ${currentDefault?.id}`);
      }
      return CLI_EXIT_CODES.SUCCESS;
    }

    const target = providers.find((p: ModelProviderConfig) => p.id === id);
    if (!target) {
      logDiagnostic(`Provider '${id}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const updated = providers.map((p: ModelProviderConfig) => ({
      ...p,
      isDefault: p.id === id,
    }));
    await persistence.saveProviders(updated);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "provider default",
        status: "success",
        data: { defaultProviderId: id },
      });
    } else {
      console.log(`Default provider set to '${id}'`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "add") {
    const idIndex = args.indexOf("--id");
    const nameIndex = args.indexOf("--name");
    const typeIndex = args.indexOf("--type");
    const modelIndex = args.indexOf("--model");
    const endpointIndex = args.indexOf("--endpoint");

    const id = idIndex >= 0 ? args[idIndex + 1] : args[1];
    const name = nameIndex >= 0 ? args[nameIndex + 1] : id;
    const type = (typeIndex >= 0 ? args[typeIndex + 1] : "openrouter") as ProviderType;
    const model = modelIndex >= 0 ? args[modelIndex + 1] : "default";
    const baseUrl = endpointIndex >= 0 ? args[endpointIndex + 1] : undefined;

    if (!id) {
      logDiagnostic("Usage: aether provider add --id <id> [--name <name>] [--type openrouter|ollama|anthropic|openai|custom]");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const newProvider: ModelProviderConfig = {
      id,
      name: name ?? id,
      type,
      baseUrl,
      credentialKeyRef: `cred:${id}`,
      credentialState: "NOT_CONFIGURED",
      models: [{ id: model, name: model }],
      selectedModel: model,
      enabled: true,
      isDefault: providers.length === 0,
    };

    const updated = [...providers.filter((p: ModelProviderConfig) => p.id !== id), newProvider];
    await persistence.saveProviders(updated);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "provider add",
        status: "success",
        data: { provider: newProvider },
      });
    } else {
      console.log(`Provider '${id}' added successfully.`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "remove" || subcommand === "rm") {
    const id = args[1];
    if (!id) {
      logDiagnostic("Missing <provider-id> for provider remove");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const updated = providers.filter((p: ModelProviderConfig) => p.id !== id);
    if (updated.length === providers.length) {
      logDiagnostic(`Provider '${id}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    await persistence.saveProviders(updated);
    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "provider remove",
        status: "success",
        data: { removedProviderId: id },
      });
    } else {
      console.log(`Provider '${id}' removed.`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "credential") {
    const id = args[1];
    const secret = args[2];
    if (!id) {
      logDiagnostic("Usage: aether provider credential <provider-id> [secret]");
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const provider = providers.find((p: ModelProviderConfig) => p.id === id);
    if (!provider) {
      logDiagnostic(`Provider '${id}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    const keyRef = provider.credentialKeyRef ?? `cred:${id}`;

    if (!secret) {
      // Check status
      const state = await persistence.getCredentialState(keyRef);
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "provider credential",
          status: "success",
          data: { providerId: id, credentialStatus: state },
        });
      } else {
        console.log(`Credential status for '${id}': ${state}`);
      }
      return CLI_EXIT_CODES.SUCCESS;
    }

    await persistence.saveSecureCredential(keyRef, secret);
    const updated = providers.map((p: ModelProviderConfig) =>
      p.id === id ? { ...p, credentialKeyRef: keyRef, credentialState: "CONFIGURED" as const } : p
    );
    await persistence.saveProviders(updated);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "provider credential",
        status: "success",
        data: { providerId: id, credentialStatus: "CONFIGURED" },
      });
    } else {
      console.log(`Credential saved securely for provider '${id}'.`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  logDiagnostic(`Unknown provider subcommand '${subcommand}' (supported: list, inspect, default, add, remove, credential)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
