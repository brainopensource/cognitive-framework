import type {
  EventEnvelope,
  MultiFileDiffModel,
  FileDiffEntry,
  MutationLifecycleState,
} from "@aether/contracts";

export function parseUnifiedDiffToFiles(
  unifiedDiff: string,
  initialStatus: MutationLifecycleState = "PROPOSED"
): FileDiffEntry[] {
  if (!unifiedDiff || !unifiedDiff.trim()) return [];

  const files: FileDiffEntry[] = [];
  const lines = unifiedDiff.split("\n");
  let currentFile: Partial<FileDiffEntry> | null = null;
  let currentPatchLines: string[] = [];

  const flushCurrent = () => {
    if (currentFile && currentFile.filePath) {
      const patchText = currentPatchLines.join("\n");
      let adds = 0;
      let dels = 0;
      for (const line of currentPatchLines) {
        if (line.startsWith("+") && !line.startsWith("+++")) adds++;
        else if (line.startsWith("-") && !line.startsWith("---")) dels++;
      }
      files.push({
        filePath: currentFile.filePath,
        oldPath: currentFile.oldPath,
        status: initialStatus,
        additions: adds,
        deletions: dels,
        patchText,
        isBinary: currentFile.isBinary ?? false,
      });
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.startsWith("diff --git ") || line.startsWith("--- a/") || (line.startsWith("--- ") && !line.startsWith("--- a/"))) {
      if (line.startsWith("diff --git ")) {
        flushCurrent();
        const parts = line.replace("diff --git ", "").trim().split(" ");
        const aPath = parts[0]?.replace(/^a\//, "") ?? "unknown";
        const bPath = parts[1]?.replace(/^b\//, "") ?? aPath;
        currentFile = { filePath: bPath, oldPath: aPath !== bPath ? aPath : undefined };
        currentPatchLines = [line];
        continue;
      } else if (!currentFile) {
        flushCurrent();
        const path = line.replace(/^--- (a\/)?/, "").trim();
        currentFile = { filePath: path };
        currentPatchLines = [line];
        continue;
      }
    }

    if (line.startsWith("+++ b/") || (line.startsWith("+++ ") && !line.startsWith("+++ b/"))) {
      const bPath = line.replace(/^\+\+\+ (b\/)?/, "").trim();
      if (currentFile) {
        currentFile.filePath = bPath;
      }
    }

    if (currentFile) {
      currentPatchLines.push(line);
    } else {
      currentFile = { filePath: "modified_file.patch" };
      currentPatchLines = [line];
    }
  }

  flushCurrent();

  if (files.length === 0 && unifiedDiff.trim().length > 0) {
    let adds = 0;
    let dels = 0;
    for (const line of lines) {
      if (line.startsWith("+") && !line.startsWith("+++")) adds++;
      else if (line.startsWith("-") && !line.startsWith("---")) dels++;
    }
    files.push({
      filePath: "patch.diff",
      status: initialStatus,
      additions: adds,
      deletions: dels,
      patchText: unifiedDiff,
      isBinary: false,
    });
  }

  return files;
}

export function reduceMultiFileDiff(events: EventEnvelope[]): MultiFileDiffModel {
  let overallStatus: MutationLifecycleState = "PROPOSED";
  let unifiedDiff = "";
  let approvalId: string | undefined = undefined;
  let isApproved = false;
  let isApplied = false;
  let isVerified = false;
  let isFailed = false;

  for (const env of events) {
    const kind = String(env.payload.kind ?? "");
    const payload = env.payload;

    if (kind === "ApprovalRequested") {
      approvalId = String(payload.approvalId ?? "");
      const diff = String(payload.unifiedDiff ?? payload.diff ?? payload.normalizedDiff ?? "");
      if (diff) {
        unifiedDiff = diff;
      }
    } else if (kind === "FileModified" || kind === "PatchGenerated") {
      const diff = String(payload.diff ?? payload.unifiedDiff ?? payload.patch ?? "");
      if (diff) {
        unifiedDiff = diff;
      }
    }

    if (kind === "ApprovalResolved") {
      if (payload.resolution === "approved") {
        isApproved = true;
      } else if (payload.resolution === "rejected") {
        isFailed = true;
      }
    }

    if (kind === "EffectDispatched" || kind === "EffectCommitted" || kind === "PatchApplied") {
      isApplied = true;
    }

    if (kind === "VerificationPassed" || kind === "TestsPassed" || (kind === "VerdictProduced" && payload.verdict === "satisfied")) {
      isVerified = true;
    }

    if (kind === "EffectFailed" || kind === "VerificationFailed" || (kind === "VerdictProduced" && payload.verdict === "failed")) {
      isFailed = true;
    }
  }

  if (isFailed) {
    overallStatus = "FAILED";
  } else if (isVerified && isApplied) {
    overallStatus = "VERIFIED";
  } else if (isApplied) {
    overallStatus = "APPLIED";
  } else if (isApproved) {
    overallStatus = "APPROVED";
  } else {
    overallStatus = "PROPOSED";
  }

  const files = parseUnifiedDiffToFiles(unifiedDiff, overallStatus);
  const totalAdditions = files.reduce((sum, f) => sum + f.additions, 0);
  const totalDeletions = files.reduce((sum, f) => sum + f.deletions, 0);

  return {
    diffId: approvalId ? `diff-${approvalId}` : "diff-current",
    approvalId,
    files,
    overallStatus,
    summary: {
      totalFiles: files.length,
      totalAdditions,
      totalDeletions,
    },
  };
}
