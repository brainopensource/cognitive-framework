export type DiffLineKind = "addition" | "deletion" | "context" | "hunk";

export type DiffLine = {
  kind: DiffLineKind;
  text: string;
  color: "green" | "red" | "gray" | "cyan";
};

export function colorizeUnifiedDiff(diff: string): DiffLine[] {
  return diff.split(/\r?\n/).filter((line) => line.length > 0).map((text) => {
    if (text.startsWith("@@") || text.startsWith("+++") || text.startsWith("---")) {
      return { kind: "hunk", text, color: "cyan" };
    }
    if (text.startsWith("+")) return { kind: "addition", text, color: "green" };
    if (text.startsWith("-")) return { kind: "deletion", text, color: "red" };
    return { kind: "context", text, color: "gray" };
  });
}
