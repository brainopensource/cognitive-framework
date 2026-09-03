"""Base Provider Protocol for LDA."""
from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from ..core.ir import ConfidenceTier, IRDocSection, IRDocument, IREntity, IRRelation, IRSymbol


class BaseProvider(ABC):
    """Abstract base provider for repository intelligence extraction."""

    name: str = "base"
    confidence_tier: ConfidenceTier = ConfidenceTier.HEURISTIC

    @abstractmethod
    def collect(
        self,
        repo_root: Path,
        incremental: bool = False,
        file_states: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Collect facts from the repository."""
        raise NotImplementedError
