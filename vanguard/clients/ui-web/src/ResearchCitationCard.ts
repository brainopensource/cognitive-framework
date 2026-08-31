import type { CitationItem } from "@aether/contracts";

export type ResearchCitationCardProps = {
  citation: CitationItem;
  onOpenLabEvidence?: (evidenceId: string) => void;
  onCopyCitation?: (text: string) => void;
};

export function renderResearchCitationCard(props: ResearchCitationCardProps): HTMLElement {
  const card = document.createElement("div");
  card.className = "aether-citation-card";
  card.style.cssText = `
    padding: 10px 14px;
    background: var(--aether-surface, #181825);
    border: 1px solid var(--aether-border, #313244);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-size: 12px;
  `;

  const topRow = document.createElement("div");
  topRow.style.cssText = "display: flex; justify-content: space-between; align-items: center;";

  const titleRow = document.createElement("div");
  titleRow.style.cssText = "font-weight: 700; color: var(--aether-accent, #89b4fa);";
  titleRow.textContent = `📖 ${props.citation.sourceTitle}`;
  topRow.appendChild(titleRow);

  if (typeof props.citation.confidence === "number") {
    const conf = document.createElement("span");
    conf.style.cssText = "font-size: 10px; padding: 2px 6px; border-radius: 4px; background: var(--aether-surface-raised, #252538); color: var(--aether-success, #a6e3a1); font-weight: 700;";
    conf.textContent = `${Math.round(props.citation.confidence * 100)}% Confidence`;
    topRow.appendChild(conf);
  }
  card.appendChild(topRow);

  if (props.citation.citationText) {
    const quote = document.createElement("div");
    quote.style.cssText = "font-style: italic; color: var(--aether-text-primary, #cdd6f4); border-left: 2px solid var(--aether-accent, #89b4fa); padding-left: 8px; font-size: 11px;";
    quote.textContent = props.citation.citationText;
    card.appendChild(quote);
  }

  // Action buttons
  const actionRow = document.createElement("div");
  actionRow.style.cssText = "display: flex; gap: 8px; margin-top: 4px; font-size: 11px;";

  const copyBtn = document.createElement("button");
  copyBtn.style.cssText = "padding: 2px 6px; background: transparent; border: 1px solid var(--aether-border, #313244); color: var(--aether-text-primary, #cdd6f4); border-radius: 4px; cursor: pointer;";
  copyBtn.textContent = "Copy Citation";
  copyBtn.onclick = () => {
    if (props.onCopyCitation) {
      props.onCopyCitation(props.citation.citationText || props.citation.sourceTitle);
    } else if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(props.citation.citationText || props.citation.sourceTitle);
    }
  };
  actionRow.appendChild(copyBtn);

  if (props.citation.evidenceAssociation && props.onOpenLabEvidence) {
    const labBtn = document.createElement("button");
    labBtn.style.cssText = "padding: 2px 6px; background: transparent; border: 1px solid var(--aether-accent, #89b4fa); color: var(--aether-accent, #89b4fa); border-radius: 4px; cursor: pointer;";
    labBtn.textContent = "Inspect Evidence in Lab ↗";
    labBtn.onclick = () => props.onOpenLabEvidence!(props.citation.evidenceAssociation!);
    actionRow.appendChild(labBtn);
  }

  card.appendChild(actionRow);
  return card;
}
