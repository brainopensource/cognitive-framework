export type SessionSummary = {
  sessionId: string;
  title: string;
  agentId: string;
  workspacePath: string;
  createdAt: string;
  updatedAt: string;
  previewText?: string;
  turnCount: number;
};

export type SessionGroup = {
  label: string;
  sessions: SessionSummary[];
};

export function groupSessionsByDate(sessions: SessionSummary[]): SessionGroup[] {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
  const yesterday = today - 86400000;
  const last7Days = today - 86400000 * 7;

  const groups: Record<string, SessionSummary[]> = {
    Today: [],
    Yesterday: [],
    "Last 7 Days": [],
    Older: [],
  };

  for (const s of sessions) {
    const time = new Date(s.updatedAt || s.createdAt).getTime();
    if (time >= today) {
      groups["Today"]!.push(s);
    } else if (time >= yesterday) {
      groups["Yesterday"]!.push(s);
    } else if (time >= last7Days) {
      groups["Last 7 Days"]!.push(s);
    } else {
      groups["Older"]!.push(s);
    }
  }

  const result: SessionGroup[] = [];
  for (const [label, list] of Object.entries(groups)) {
    if (list.length > 0) {
      result.push({
        label,
        sessions: list.sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()),
      });
    }
  }

  return result;
}

export function filterSessions(sessions: SessionSummary[], query: string): SessionSummary[] {
  if (!query.trim()) return sessions;
  const q = query.toLowerCase();
  return sessions.filter(
    (s) =>
      s.title.toLowerCase().includes(q) ||
      (s.previewText && s.previewText.toLowerCase().includes(q)) ||
      s.agentId.toLowerCase().includes(q) ||
      s.workspacePath.toLowerCase().includes(q)
  );
}
