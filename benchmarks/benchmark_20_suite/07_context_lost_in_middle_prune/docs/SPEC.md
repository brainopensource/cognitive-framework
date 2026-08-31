# Specification: Lost-in-the-Middle Context Pruning (CTX-07)

When `ContextAllocator.prune_section(header, docstring, body_lines, max_lines)` is called:
1. `header` and `docstring` MUST always be anchored at the beginning of the returned string.
2. The middle of `body_lines` is compressed with `# ... [pruned] ...`.
3. The top and bottom slices of `body_lines` are preserved up to `max_lines`.
