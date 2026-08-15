import { createInterface } from "node:readline/promises";
import { stdin, stdout } from "node:process";

import { GitPatchEnvironment } from "./git-environment.ts";
import { OpenAiCompatibleSliceProvider } from "./provider.ts";
import { runSlice } from "./workflow.ts";

const endpoint = process.env.VG_SLICE_ENDPOINT;
const apiKey = process.env.VG_SLICE_API_KEY;
const model = process.env.VG_SLICE_MODEL;
const repository = process.env.VG_SLICE_REPO;
const task = process.env.VG_SLICE_TASK;
const rawTestArgv = process.env.VG_SLICE_TEST_ARGV;

if (!endpoint || !apiKey || !model || !repository || !task || !rawTestArgv) {
  console.error("VG_SLICE_ENDPOINT, VG_SLICE_API_KEY, VG_SLICE_MODEL, VG_SLICE_REPO, VG_SLICE_TASK and VG_SLICE_TEST_ARGV are required; no request was made.");
  process.exitCode = 2;
} else {
  let testArgv: unknown;
  try { testArgv = JSON.parse(rawTestArgv); }
  catch { testArgv = undefined; }
  if (!Array.isArray(testArgv) || !testArgv.every((item) => typeof item === "string") || testArgv.length === 0) {
    console.error('VG_SLICE_TEST_ARGV must be a non-empty JSON string array, for example ["python3","-m","unittest"].');
    process.exitCode = 2;
  } else {
    const provider = new OpenAiCompatibleSliceProvider({ endpoint, apiKey, model }, fetch as never);
    const environment = await GitPatchEnvironment.open(repository);
    const result = await runSlice({ task, testArgv }, provider, environment, async (preview) => {
      console.log(`\nProposed patch:\n${preview.patch}\nPatch summary:\n${preview.summary}\n`);
      const prompt = createInterface({ input: stdin, output: stdout });
      try { return (await prompt.question('Type "approve" to apply and run tests: ')).trim() === "approve"; }
      finally { prompt.close(); }
    });
    // Provider credentials and unbounded provider response bodies are never emitted.
    console.log(JSON.stringify(result.outcome === "applied" || result.outcome === "tests_failed"
      ? { outcome: result.outcome, testExitCode: result.test.exitCode, stdout: result.test.stdout, stderr: result.test.stderr }
      : result));
    if (result.outcome !== "applied" && result.outcome !== "rejected") process.exitCode = 1;
  }
}
