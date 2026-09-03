from typing import List, Dict

class ContextAllocator:
    @staticmethod
    def prune_section(header: str, docstring: str, body_lines: List[str], max_lines: int) -> str:
        """Prunes content using lost-in-the-middle strategy, preserving header and docstring."""
        if len(body_lines) <= max_lines:
            return f"{header}\n{docstring}\n" + "\n".join(body_lines)

        # BUG: Slices from start and drops the header/docstring when truncating!
        pruned_body = body_lines[:max_lines // 2] + ["# ... [pruned] ..."] + body_lines[-(max_lines // 2):]
        # Buggy implementation drops header and docstring from returned output:
        return "\n".join(pruned_body)
