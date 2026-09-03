import type { ParsedCli } from "../composition/parse-cli.js";
import { NodeFsPersistenceAdapter, DEFAULT_PROVIDERS } from "@aether/client";
import type { ModelProviderConfig, ModelDescriptor } from "@aether/contracts";
import {
  CLI_EXIT_CODES,
  logDiagnostic,
  writeJsonOutcome,
} from "../output.js";

export async function handleModel(args: string[], options: ParsedCli): Promise<number> {
  const persistence = new NodeFsPersistenceAdapter();
  const subcommand = args[0] || "list";

  let providers: ModelProviderConfig[] = (await persistence.loadProviders()) ?? [];
  if (providers.length === 0) {
    providers = DEFAULT_PROVIDERS;
    await persistence.saveProviders(providers);
  }

  const defaultProvider = providers.find((p: ModelProviderConfig) => p.isDefault) ?? providers[0];

  if (subcommand === "list") {
    const providerId = args[1] ?? defaultProvider?.id;
    const provider = providers.find((p: ModelProviderConfig) => p.id === providerId);
    if (!provider) {
      logDiagnostic(`Provider '${providerId}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "model list",
        status: "success",
        data: {
          providerId: provider.id,
          selectedModel: provider.selectedModel,
          models: provider.models,
        },
      });
    } else {
      console.log(`\nAvailable Models for '${provider.name}' (${provider.models.length}):`);
      for (const m of provider.models) {
        const isCurrent = m.id === provider.selectedModel ? " (selected)" : "";
        console.log(`  ${m.id.padEnd(32)} ${m.name}${isCurrent}`);
      }
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  if (subcommand === "default" || subcommand === "set") {
    let providerId: string;
    let modelId: string;

    if (args.length >= 3) {
      providerId = args[1]!;
      modelId = args[2]!;
    } else if (args.length === 2) {
      providerId = defaultProvider?.id ?? "provider-openrouter";
      modelId = args[1]!;
    } else {
      if (options.json) {
        writeJsonOutcome({
          api: "aether.cli-outcome/1",
          command: "model default",
          status: "success",
          data: {
            providerId: defaultProvider?.id,
            selectedModel: defaultProvider?.selectedModel,
          },
        });
      } else {
        console.log(`Default model: ${defaultProvider?.selectedModel} (on provider '${defaultProvider?.id}')`);
      }
      return CLI_EXIT_CODES.SUCCESS;
    }

    const provider = providers.find((p: ModelProviderConfig) => p.id === providerId);
    if (!provider) {
      logDiagnostic(`Provider '${providerId}' not found`);
      return CLI_EXIT_CODES.INVALID_INPUT;
    }

    // Add model to list if not present
    const modelExists = provider.models.some((m: ModelDescriptor) => m.id === modelId);
    const updatedModels = modelExists ? provider.models : [...provider.models, { id: modelId, name: modelId }];

    const updated = providers.map((p: ModelProviderConfig) =>
      p.id === providerId
        ? { ...p, selectedModel: modelId, models: updatedModels }
        : p
    );
    await persistence.saveProviders(updated);

    if (options.json) {
      writeJsonOutcome({
        api: "aether.cli-outcome/1",
        command: "model set",
        status: "success",
        data: { providerId, selectedModel: modelId },
      });
    } else {
      console.log(`Model set to '${modelId}' on provider '${providerId}'.`);
    }
    return CLI_EXIT_CODES.SUCCESS;
  }

  logDiagnostic(`Unknown model subcommand '${subcommand}' (supported: list, default, set)`);
  return CLI_EXIT_CODES.INVALID_INPUT;
}
