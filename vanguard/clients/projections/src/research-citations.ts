import type {
  EventEnvelope,
  ResearchProgressSummary,
  CitationItem,
} from "@aether/contracts";

export function reduceResearchSummary(events: EventEnvelope[]): ResearchProgressSummary {
  const citations: CitationItem[] = [];
  let verifiedClaims = 0;
  let activeRetrievals = 0;
  let synthesisText: string | undefined = undefined;

  for (const env of events) {
    const kind = String(env.payload.kind ?? "");
    const payload = env.payload;
    const eventId = env.eventId;

    if (kind === "SearchExecuted" || kind === "RetrievalStarted") {
      activeRetrievals++;
    } else if (kind === "RetrievalCompleted") {
      if (activeRetrievals > 0) activeRetrievals--;
    }

    if (kind === "CitationAdded" || kind === "SourceCited" || (kind === "ClaimRecorded" && payload.sourceUrl)) {
      const url = String(payload.sourceUrl ?? payload.url ?? payload.origin ?? "unknown");
      const title = String(payload.sourceTitle ?? payload.title ?? url);
      const text = String(payload.citationText ?? payload.quote ?? payload.statement ?? "");
      const claim = typeof payload.claim === "string" ? payload.claim : typeof payload.statement === "string" ? payload.statement : undefined;
      const evidence = typeof payload.evidenceId === "string" ? payload.evidenceId : typeof payload.evidenceDigest === "string" ? payload.evidenceDigest : undefined;
      const confidence = typeof payload.confidence === "number" ? payload.confidence : undefined;
      const uncertaintyNotes = typeof payload.uncertainty === "string" ? payload.uncertainty : typeof payload.caveats === "string" ? payload.caveats : undefined;
      const artifactRef = typeof payload.artifactId === "string" ? payload.artifactId : undefined;

      citations.push({
        id: `cite-${eventId}`,
        sourceTitle: title,
        sourceOrigin: url,
        citationText: text,
        claimAssociation: claim,
        evidenceAssociation: evidence,
        confidence,
        uncertaintyNotes,
        artifactRef,
      });
    }

    if (kind === "ClaimVerified" || (kind === "ClaimRecorded" && payload.verified === true)) {
      verifiedClaims++;
    }

    if (kind === "SynthesisProduced" || kind === "ReportGenerated") {
      const syn = typeof payload.summary === "string" ? payload.summary : typeof payload.content === "string" ? payload.content : typeof payload.text === "string" ? payload.text : undefined;
      if (syn) {
        synthesisText = syn;
      }
    }
  }

  return {
    totalSources: citations.length,
    verifiedClaims,
    activeRetrievals,
    citations,
    synthesisText,
  };
}
