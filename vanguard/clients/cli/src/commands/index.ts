import type { ParsedCli } from "../composition/parse-cli.js";
import { handleInit } from "./init.js";
import { handleAgent } from "./agent.js";
import { handleComposition } from "./composition.js";
import { handleEvent } from "./event.js";
import { handleArtifact } from "./artifact.js";
import { handleSchema } from "./schema.js";
import { handleLineage } from "./lineage.js";
import {
  handleRun,
  handleCode,
  handleExplain,
  handleDoctor,
  handleApprove,
  handleResume,
  handleTrace,
  handleWhy,
  handleDaemon,
} from "./legacy.js";

export type CommandHandler = (args: string[], options: ParsedCli) => Promise<number>;

export const COMMANDS: Record<string, CommandHandler> = {
  run: handleRun,
  code: handleCode,
  explain: handleExplain,
  doctor: handleDoctor,
  approve: handleApprove,
  resume: handleResume,
  trace: handleTrace,
  why: handleWhy,
  daemon: handleDaemon,
  init: handleInit,
  agent: handleAgent,
  composition: handleComposition,
  event: handleEvent,
  artifact: handleArtifact,
  schema: handleSchema,
  lineage: handleLineage,
};
