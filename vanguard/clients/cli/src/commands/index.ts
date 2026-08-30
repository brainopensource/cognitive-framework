import type { ParsedCli } from "../composition/parse-cli.js";
import { handleRun } from "./run.js";
import { handleAgent } from "./agent.js";
import { handleWorkflow } from "./workflow.js";
import { handleArtifact } from "./artifact.js";
import { handleEvent } from "./event.js";
import { handleApprove } from "./approve.js";
import { handleDoctor } from "./doctor.js";
import { handleDaemon } from "./daemon.js";
import { handleInit } from "./init.js";
import { handleComposition } from "./composition.js";
import { handleSchema } from "./schema.js";
import { handleLineage } from "./lineage.js";
import {
  handleCode,
  handleExplain,
  handleResume,
  handleTrace,
  handleWhy,
} from "./legacy.js";

export type CommandHandler = (args: string[], options: ParsedCli) => Promise<number>;

export const COMMANDS: Record<string, CommandHandler> = {
  run: handleRun,
  agent: handleAgent,
  workflow: handleWorkflow,
  artifact: handleArtifact,
  event: handleEvent,
  approve: handleApprove,
  doctor: handleDoctor,
  daemon: handleDaemon,
  code: handleCode,
  explain: handleExplain,
  resume: handleResume,
  trace: handleTrace,
  why: handleWhy,
  init: handleInit,
  composition: handleComposition,
  schema: handleSchema,
  lineage: handleLineage,
};
