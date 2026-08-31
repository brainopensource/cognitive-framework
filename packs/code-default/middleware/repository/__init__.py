"""Repository intelligence middleware package."""

from .context_ranker import RankedReference, RankingWeights, rank_repository_context
from .import_graph import FileDependencies, extract_file_imports
from .multi_file_completeness import (
    CodeDefaultCompletionPolicy,
    CompletenessPolicy,
    CompletionPolicy,
    CompletenessReport,
    check_multi_file_completeness,
)
from .greenfield import GreenfieldAssessment, GreenfieldPolicy, ScaffoldBaseline, assess_greenfield_workspace
from .symbol_indexer import SymbolDefinition, index_python_source
from .task_classifier import TaskClassification, TaskClassifier, TaskKind, classify_task
from .implicated_files import ImplicatedFile, ImplicatedFileSet, ImplicatedFileSetBuilder, build_implicated_file_set

__all__ = [
    "SymbolDefinition",
    "index_python_source",
    "FileDependencies",
    "extract_file_imports",
    "RankedReference",
    "RankingWeights",
    "rank_repository_context",
    "CompletenessReport",
    "check_multi_file_completeness",
    "CodeDefaultCompletionPolicy",
    "CompletionPolicy",
    "CompletenessPolicy",
    "GreenfieldAssessment",
    "GreenfieldPolicy",
    "ScaffoldBaseline",
    "assess_greenfield_workspace",
    "TaskKind",
    "TaskClassification",
    "TaskClassifier",
    "classify_task",
    "ImplicatedFile",
    "ImplicatedFileSet",
    "ImplicatedFileSetBuilder",
    "build_implicated_file_set",
]
