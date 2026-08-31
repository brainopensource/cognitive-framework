# Greenfield PRD: Structured Markdown Section Chunker

## Objective
Implement `MarkdownSectionSplitter` and `MarkdownChunk` in `src/splitter.py`.

## Requirements
- `MarkdownChunk(title: str, level: int, breadcrumbs: list[str], content: str, token_estimate: int)`
- `MarkdownSectionSplitter.split(markdown_text: str, max_tokens: int = 500) -> list[MarkdownChunk]`
- Splits along headers (`#`, `##`, `###`), tracking `breadcrumbs` (e.g. `["Architecture", "Kernel", "Dispatch"]`).
- Ignores `#` characters inside fenced code blocks (` ```...``` `).
- Preserves headers and section bodies.
